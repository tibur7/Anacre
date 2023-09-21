-- SQL query to check distinct combinations of ObservedAgentIdentifier and ProtectionIdentifier
-- in both ProtectionReceived and InstrumentProtectionReceived
-- and include error messages from record_rules

-- Create a temporary table to store the distinct combinations from ProtectionReceived
CREATE TEMPORARY TABLE DistinctCombinationsPR AS
SELECT DISTINCT
    ObservedAgentIdentifier,
    ProtectionIdentifier
FROM
    ProtectionReceived;

-- Create a temporary table to store the distinct combinations from InstrumentProtectionReceived
CREATE TEMPORARY TABLE DistinctCombinationsIPR AS
SELECT DISTINCT
    ObservedAgentIdentifier,
    ProtectionIdentifier
FROM
    InstrumentProtectionReceived;

-- Create a temporary table to store the validation results
CREATE TEMPORARY TABLE ValidationResults AS
SELECT
    dcpr.ObservedAgentIdentifier AS ObservedAgentIdentifier_PR,
    dcpr.ProtectionIdentifier AS ProtectionIdentifier_PR,
    CASE
        WHEN dcipr.ObservedAgentIdentifier IS NULL THEN 'False' -- Not in InstrumentProtectionReceived
        ELSE 'True' -- Exists in InstrumentProtectionReceived
    END AS Correct,
    rr.RuleDescription AS ErrorMessage
FROM
    DistinctCombinationsPR dcpr
LEFT JOIN
    DistinctCombinationsIPR dcipr
ON
    dcpr.ObservedAgentIdentifier = dcipr.ObservedAgentIdentifier
    AND dcpr.ProtectionIdentifier = dcipr.ProtectionIdentifier
LEFT JOIN
    record_rules rr
ON
    rr.RuleNumber = 'RI0250'; -- Assuming RI0250 is the rule number you're checking

-- Select the results
SELECT * FROM ValidationResults;


