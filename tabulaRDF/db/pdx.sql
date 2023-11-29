CREATE SCHEMA IF NOT EXISTS pdx;
-- Creates new user defined type 'mood' as an Enum
CREATE TYPE pdx_sources AS ENUM ('GB',
                                'CHAMPIONS',
                                'CHARLESRIVER',
                                'CROWNBIO',
                                'DANA-FARBER CANCER INSTITUTE',
                                'GENENDESIGN',
                                'GHP'
                                );

-- This will fail since the mood type already exists
CREATE TYPE analysis_type AS ENUM ('DNASEQ',
                                    'RNASEQ',
                                    'TPX',
                                    'WPX',
                                    'ATACSEQ'
                                    );

CREATE TYPE biotype AS ENUM ('DNA',
                            'RNA',
                            'PROT'
                            );
-- This will fail since Enums cannot hold null values
CREATE TYPE ethnicity AS ENUM ('ASIAN',
                                'BLACK',
                                'CAUCASIAN',
                                'LATINO');

-- This will fail since Enum values must be unique
CREATE TYPE gender AS ENUM ('M',
                            'F',
                            'NB');

-- Grade
CREATE TYPE tumor_grade AS ENUM ('I',
                            'II',
                            'III',
                            'IV',
                            'V');

CREATE TYPE tumor_stage AS ENUM ('I',
                            'II',
                            'III',
                            'IV',
                            'V');

CREATE TYPE tumor_type_acronym AS ENUM ('NSCLC');

CREATE TYPE lab_qc AS ENUM ('FAIL', 'PASS');

CREATE TYPE az_data_qc_reason AS ENUM ('RELEASED');

CREATE TYPE remediation AS ENUM ('REMEDIATION');

-- create a schema

-- create a schema if it does not exist yet

DROP TABLE IF EXISTS pdx.model;
CREATE TABLE pdx.model(
    id INTEGER PRIMARY KEY,
    model_name VARCHAR(255) UNIQUE NOT NULL,
    model_source VARCHAR(255) NOT NULL,
    biopsy_site VARCHAR(255),
    patient_ethnicity ethnicity,
    patient_gender gender,
    tumor_grade tumor_grade,
    tumor_stage tumor_stage,
    tumor_type tumor_type_acronym,
    tumor_pathology_diagnosis VARCHAR(255),
    treatment_history VARCHAR(255),
    );

DROP TABLE IF EXISTS pdx.sample;
CREATE TABLE pdx.sample(
    id INTEGER PRIMARY KEY,
    sample_name VARCHAR(255) UNIQUE NOT NULL,
    model_name VARCHAR(255),
    mouse_id VARCHAR(30) NOT NULL,
    tumor_passage VARCHAR(3) NOT NULL,
    analysis_type analysis_type,
    batch INTEGER NOT NULL,
    tumor_sample_source VARCHAR(255) NOT NULL,
    sample_biotype biotype,
    project_name VARCHAR(255),
    FOREIGN KEY (model_name) REFERENCES pdx.model(model_name)
    );

DROP TABLE IF EXISTS pdx.rna_sample_lab_qc;
CREATE TABLE pdx.rna_sample_lab_qc(
    id INTEGER PRIMARY KEY,
    sample_name VARCHAR(255),
    -- sammple_uuid VARCHAR(255) NOT,
    sample_biotype CHAR(3) CHECK (sample_biotype = 'RNA'),
    az_concentration FLOAT, --(ng/ul)
    az_volume FLOAT, --(ul)
    az_total_amount FLOAT, --(ng)
    az_rin FLOAT,
    az_extraction_date DATE,
    az_lab_qc lab_qc,
    lab_provider VARCHAR(30) NOT NULL,
    provider_rna_conc FLOAT, --(ng/ul)
    provider_volume FLOAT, --(ul)
    provider_total_amount FLOAT, --(ug)
    provider_rin FLOAT,
    provider_qc lab_qc,
    provider_data_delivery DATE,
    provider_comments TEXT,
    az_data_qc lab_qc,
    az_data_qc_reason az_data_qc_reason,
    remediation remediation,
    jira_ticket_url VARCHAR(60),
    FOREIGN KEY (sample_name) REFERENCES pdx.sample(sample_name)
    );

DROP TABLE IF EXISTS pdx.dna_sample_lab_qc;
CREATE TABLE pdx.dna_sample_lab_qc(
    id INTEGER PRIMARY KEY,
    sample_name VARCHAR(255),
    -- sample_uuid
    sample_biotype CHAR(3) CHECK (sample_biotype = 'DNA'),
    az_concentration FLOAT, --(ng/ul)
    az_volume FLOAT, --(ul)
    az_total_amount FLOAT, --(ng)
    az_din FLOAT,
    az_extraction_date DATE,
    az_lab_qc lab_qc,
    lab_provider VARCHAR(30) NOT NULL,
    provider_dna_conc FLOAT, --(ng/ul)
    provider_volume FLOAT, --(ul)
    provider_total_amount FLOAT, --(ug)
    provider_qc lab_qc,
    provider_data_delivery DATE,
    provider_comments TEXT,
    az_data_qc lab_qc,
    az_data_qc_reason az_data_qc_reason,
    remediation remediation,
    jira_ticket_url VARCHAR(60),
    FOREIGN KEY (sample_name) REFERENCES pdx.sample(sample_name)
    );

DROP TABLE IF EXISTS pdx.tp_sample_lab_qc;
CREATE TABLE pdx.tp_sample_lab_qc(
    id INTEGER PRIMARY KEY,
    sample_name VARCHAR(255),
    sample_biotype CHAR(3) CHECK (sample_biotype = 'TPX'),
    az_concentration FLOAT, --(ng/ul)
    micro_bca FLOAT, --(ul)
    area FLOAT, --(ng)
    cell_count INTEGER,
    sample_prep_sop VARCHAR(100),
    sample_prep_date DATE,
    az_data_qc lab_qc,
    az_data_qc_reason az_data_qc_reason,
    remediation remediation,
    FOREIGN KEY (sample_name) REFERENCES pdx.sample(sample_name)
    );

-- CREATE TABLE pdx.wes_seq2c();

-- CREATE TABLE pdx.wes_vardict();

-- CREATE TABLE pdx.wes_cnv();

-- CREATE TABLE pdx.rna_tpm();

-- CREATE TABLE pdx.tpx_quantitation();
