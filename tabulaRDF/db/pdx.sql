CREATE DATABASE pdx;
USE pdx;
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

CREATE TYPE significance as ENUM('KNOWN', 'UNKNOWN');

CREATE TYPE variant_type as ENUM('COPY-NUMBER-ALTERATION')


DROP TABLE IF EXISTS model;
CREATE TABLE model(
    id CHAR(55) PRIMARY KEY,
    model_name CHAR(55) UNIQUE NOT NULL,
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

DROP TABLE IF EXISTS sample;
CREATE TABLE sample(
    id CHAR(55) PRIMARY KEY,
    sample_name CHAR(55) UNIQUE NOT NULL,
    model_name CHAR(55),
    mouse_id VARCHAR(30) NOT NULL,
    tumor_passage VARCHAR(3) NOT NULL,
    analysis_type analysis_type,
    batch INTEGER NOT NULL,
    tumor_sample_source VARCHAR(255) NOT NULL,
    sample_biotype biotype,
    project_name VARCHAR(255),
    FOREIGN KEY (model_name) REFERENCES model(model_name),
    KEY (model_name, sample_biotype)
    );

DROP TABLE IF EXISTS rna_sample_lab_qc;
CREATE TABLE rna_sample_lab_qc(
    id CHAR(55) PRIMARY KEY,
    sample_name UNIQUE CHAR(55),
    sample_biotype CHAR(3) CHECK (sample_biotype = 'RNA'),
    az_concentration FLOAT,
    az_volume FLOAT,
    az_total_amount FLOAT,
    az_rin FLOAT,
    az_extraction_date DATE,
    az_lab_qc lab_qc,
    lab_provider VARCHAR(30) NOT NULL,
    provider_rna_conc FLOAT,
    provider_volume FLOAT,
    provider_total_amount FLOAT,
    provider_rin FLOAT,
    provider_qc lab_qc,
    provider_data_delivery DATE,
    provider_comments TEXT,
    az_data_qc lab_qc,
    az_data_qc_reason az_data_qc_reason,
    remediation remediation,
    jira_ticket_url VARCHAR(60),
    FOREIGN KEY (sample_name) REFERENCES sample(sample_name),
    FOREIGN KEY (sample_biotype) REFERENCES sample(sample_biotype)

    );

DROP TABLE IF EXISTS dna_sample_lab_qc;
CREATE TABLE dna_sample_lab_qc(
    id CHAR(55) PRIMARY KEY,
    sample_name UNIQUE CHAR(55),
    sample_biotype CHAR(3) CHECK (sample_biotype = 'DNA'),
    az_concentration FLOAT,
    az_volume FLOAT,
    az_total_amount FLOAT,
    az_din FLOAT,
    az_extraction_date DATE,
    az_lab_qc lab_qc,
    lab_provider VARCHAR(30) NOT NULL,
    provider_dna_conc FLOAT,
    provider_volume FLOAT,
    provider_total_amount FLOAT,
    provider_qc lab_qc,
    provider_data_delivery DATE,
    provider_comments TEXT,
    az_data_qc lab_qc,
    az_data_qc_reason az_data_qc_reason,
    remediation remediation,
    jira_ticket_url VARCHAR(60),
    FOREIGN KEY (sample_name) REFERENCES sample(sample_name),
    FOREIGN KEY (sample_biotype) REFERENCES sample(sample_biotype)
    );

DROP TABLE IF EXISTS tp_sample_lab_qc;
CREATE TABLE tp_sample_lab_qc(
    id CHAR(55) PRIMARY KEY,
    sample_name UNIQUE CHAR(55),
    sample_biotype CHAR(3) CHECK (sample_biotype = 'TPX'),
    az_concentration FLOAT,
    micro_bca FLOAT,
    area FLOAT,
    cell_count INTEGER,
    sample_prep_sop VARCHAR(100),
    sample_prep_date DATE,
    az_data_qc lab_qc,
    az_data_qc_reason az_data_qc_reason,
    remediation remediation,
    FOREIGN KEY (sample_name) REFERENCES sample(sample_name),
    FOREIGN KEY (sample_biotype) REFERENCES sample(sample_biotype)
    );

DROP TABLE IF EXISTS seq2c;
CREATE TABLE seq2c(
    id CHAR(55) PRIMARY KEY,
    sample_name CHAR(55) NOT NULL,
    model_name CHAR(55) NOT NULL,
    chromosome VARCHAR(5) NOT NULL,
    coordinate VARCHAR(30) NOT NULL,
    cnv VARCHAR(30) NOT NULL,
    cnv_segment VARCHAR(30) NOT NULL,
    cnv_type VARCHAR(30) NOT NULL,
    copy_number VARCHAR(30) NOT NULL,
    gene VARCHAR(30) NOT NULL,
    log_ratio DOUBLE,
    significance significance,
    variant_type variant_type,
    FOREIGN KEY (sample_name) REFERENCES sample(sample_name),
    FOREIGN KEY (model_name) REFERENCES sample(model_name),
    );


DROP TABLE IF EXISTS vardict;
CREATE TABLE vardict(
    id CHAR(55) PRIMARY KEY,
    sample_name CHAR(55) NOT NULL,
    model_name CHAR(55) NOT NULL,
    chromosome VARCHAR(5) NOT NULL,
    variant_start INTEGER,
    variant_id VARCHAR,
    ref_sequence VARCHAR,
    alt_sequence VARCHAR,
    variant_type VARCHAR,
    variant_effect VARCHAR,
    functional_class VARCHAR,
    codon_change VARCHAR,
    amino_acid_change VARCHAR,
    cdna_change VARCHAR,
    amino_acid_length VARCHAR,
    gene VARCHAR,
    transcript_biotype VARCHAR,
    gene_coding VARCHAR,
    transcript VARCHAR,
    exon VARCHAR,
    cosmic_gene VARCHAR,
    cosmic_cds_change VARCHAR,
    cosmic_aa_change VARCHAR,
    cosmic_cnt VARCHAR,
    depth VARCHAR,
    allelefreq VARCHAR,
    bias VARCHAR,
    pmean VARCHAR,
    pstd VARCHAR,
    qual VARCHAR,
    qstd VARCHAR,
    sbf VARCHAR,
    gmaf VARCHAR,
    vd VARCHAR,
    rd VARCHAR,
    clnsig VARCHAR,
    cln_gene VARCHAR,
    oddratio VARCHAR,
    hiaf VARCHAR,
    mq VARCHAR,
    sn VARCHAR,
    adjaf VARCHAR,
    nm VARCHAR,
    shift3 VARCHAR,
    msi VARCHAR,
    gt VARCHAR,
    duprate VARCHAR,
    splitreads VARCHAR,
    spanpairs VARCHAR,
    lof FLOAT,
    dkfzbias VARCHAR,
    n_samples INTEGER,
    n_var INTEGER,
    pcnt_sample FLOAT,
    ave_af FLOAT,
    pass VARCHAR,
    var_type VARCHAR,
    var_class VARCHAR,
    significance VARCHAR,
    reason VARCHAR,
    incidentalome VARCHAR,
    actionability_tier VARCHAR,
    actionability_type VARCHAR,
    annotation_index VARCHAR,
    chip_category VARCHAR,
    cosmic_id VARCHAR,
    dbsnp_rsids VARCHAR,
    gene_region_codon VARCHAR,
    genome_build VARCHAR,
    genomic_coordinates_build VARCHAR,
    genomic_coordinates_chromosome VARCHAR,
    genomic_coordinates_start VARCHAR,
    genomic_coordinates_stop VARCHAR,
    gnomad_af VARCHAR,
    gnomad_af_popmax VARCHAR,
    gnomad_popmax VARCHAR,
    incidentalome_list VARCHAR,
    is_actionable VARCHAR,
    max_af VARCHAR,
    msi_unit_length VARCHAR,
    nuc_change_len VARCHAR,
    poa_panels VARCHAR,
    poa_panels_prevalence VARCHAR,
    poa_panels_prevalence_sureselect VARCHAR,
    pon_panels VARCHAR,
    protein_change VARCHAR,
    reason_list VARCHAR,
    regex_az_lof VARCHAR,
    sample_genome VARCHAR,
    significance_list VARCHAR,
    source_filename VARCHAR,
    source_project VARCHAR,
    variant VARCHAR,
    artifacts VARCHAR,
    dbsnpbuildid VARCHAR,
    variant_end INTEGER,
    exac_af FLOAT,
    variant_filter VARCHAR,
    reject VARCHAR,
    variant_status VARCHAR,
    strand_bias_support VARCHAR,
    FOREIGN KEY (sample_name) REFERENCES sample(sample_name),
    FOREIGN KEY (model_name) REFERENCES sample(model_name)
    );

DROP TABLE IF EXISTS tpm_prm;
CREATE TABLE tpm_prm(
    id CHAR(55) PRIMARY KEY,
    sample_name CHAR(50),
    transition VARCHAR,
    peptide VARCHAR,
    peptide_curation BOOLEAN,
    preferred VARCHAR,
    hugo_gene VARCHAR,
    conc FLOAT,
    lloq FLOAT,
    uniprot_id VARCHAR,
    collection_method VARCHAR,
    date_of_digestion DATE,
    histology_id VARCHAR,
    tissue_format VARCHAR,
    micro_bca FLOAT,
    project VARCHAR,
    source VARCHAR,
    panel VARCHAR,
    model_name VARCHAR(50),
    indication VARCHAR,
    FOREIGN KEY (sample_name) REFERENCES sample(sample_name),
    FOREIGN KEY (model_name) REFERENCES sample(model_name)
    );
-- CREATE TABLE pdx.wes_seq2c();

-- CREATE TABLE pdx.wes_vardict();

-- CREATE TABLE pdx.wes_cnv();

-- CREATE TABLE pdx.rna_tpm();

-- CREATE TABLE pdx.tpx_quantitation();
