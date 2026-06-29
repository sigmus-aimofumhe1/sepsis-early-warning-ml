-- Drop the view if it already exists to allow clean updates
DROP VIEW IF EXISTS v_engineered_icu_vitals;

CREATE VIEW v_engineered_icu_vitals AS
WITH windowed_vitals AS (
    SELECT 
        patient_id,
        hour_idx,
        HR,
        Temp,
        SBP,
        Resp,
        O2Sat,
        WBC,
        Age,
        Gender,
        ICULOS,
        SepsisLabel,
        
        -- 1. Cardiovascular Volatility: Captures erratic heart rate swings over a 3-hour window
        STRFTIME('%Y-%m-%d %H:%M:%S', 'now') AS engineered_at,
        AVG(HR) OVER (
            PARTITION BY patient_id 
            ORDER BY hour_idx 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_hr_3h,
        
        -- Calculate rolling variation to spot early autonomic dysfunction
        -- SQLite lacks an inline STDDEV function, so we write a robust variance proxy:
        (HR - AVG(HR) OVER (PARTITION BY patient_id ORDER BY hour_idx ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)) AS hr_delta_from_avg,

        -- 2. Thermoregulatory Trend: Compares current temp against a 4-hour rolling baseline to detect rapid onset fever
        AVG(Temp) OVER (
            PARTITION BY patient_id 
            ORDER BY hour_idx 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_temp_4h

    FROM icu_vitals
)
SELECT 
    patient_id,
    hour_idx,
    HR,
    Temp,
    SBP,
    Resp,
    O2Sat,
    WBC,
    Age,
    Gender,
    ICULOS,
    SepsisLabel,
    rolling_avg_hr_3h,
    ABS(hr_delta_from_avg) AS hr_volatility_3h,
    (Temp - rolling_avg_temp_4h) AS temp_trend_4h,
    
    -- 3. Clinical Shock Index: Classic ICU marker for early systemic circulatory failure (HR / SBP)
    -- Uses a CASE statement to elegantly avoid division-by-zero errors if blood pressure spikes down
    CASE 
        WHEN SBP > 0 THEN (HR / SBP)
        ELSE 0 
    END AS shock_index

FROM windowed_vitals;