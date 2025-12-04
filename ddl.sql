USE cs122a_project;
DROP TABLE IF EXISTS Configuration_Uses_CustomizedModel;
DROP TABLE IF EXISTS Utilize;
DROP TABLE IF EXISTS LLMService;
DROP TABLE IF EXISTS DataStorageService;
DROP TABLE IF EXISTS InternetService;
DROP TABLE IF EXISTS Configuration;
DROP TABLE IF EXISTS CustomizedModel;
DROP TABLE IF EXISTS BaseModel;
DROP TABLE IF EXISTS AgentClient;
DROP TABLE IF EXISTS AgentCreator;
DROP TABLE IF EXISTS User;

------------------------------------------------------------
-- Q1: User and Agent Creator/Client (Entities)
------------------------------------------------------------
CREATE TABLE User (
    uid INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    PRIMARY KEY (uid),
    UNIQUE KEY uq_user_username (username),
    UNIQUE KEY uq_user_email (email)
);

CREATE TABLE AgentCreator (
    uid INT NOT NULL,
    payout_account VARCHAR(100),
    bio TEXT,
    PRIMARY KEY (uid),
    CONSTRAINT fk_agentcreator_user
        FOREIGN KEY (uid) REFERENCES User(uid)
);

CREATE TABLE AgentClient (
    uid INT NOT NULL,
    card_number CHAR(16) NOT NULL,
    card_holder_name VARCHAR(100) NOT NULL,
    expiration_date CHAR(5) NOT NULL,  -- e.g. '12/28'
    cvv CHAR(4) NOT NULL,
    zip VARCHAR(10) NOT NULL,
    interests VARCHAR(255),
    PRIMARY KEY (uid),
    CONSTRAINT fk_agentclient_user
        FOREIGN KEY (uid) REFERENCES User(uid)
);

------------------------------------------------------------
-- Q2: Base and Customized Model (Entities)
------------------------------------------------------------
CREATE TABLE BaseModel (
    bmid INT NOT NULL,
    description TEXT,
    creator_uid INT NOT NULL,
    PRIMARY KEY (bmid),
    CONSTRAINT fk_basemodel_creator
        FOREIGN KEY (creator_uid) REFERENCES AgentCreator(uid)
);

CREATE TABLE CustomizedModel (
    bmid INT NOT NULL,
    mid INT NOT NULL,
    PRIMARY KEY (bmid, mid),
    CONSTRAINT fk_customizedmodel_basemodel
        FOREIGN KEY (bmid) REFERENCES BaseModel(bmid)
        ON DELETE CASCADE
);

------------------------------------------------------------
-- Q3: Configuration (Entities)
------------------------------------------------------------
CREATE TABLE Configuration (
    cid INT NOT NULL,
    label VARCHAR(100),
    content TEXT,
    client_uid INT NOT NULL,
    PRIMARY KEY (cid),
    CONSTRAINT fk_configuration_client
        FOREIGN KEY (client_uid) REFERENCES AgentClient(uid)
);

------------------------------------------------------------
-- Q4: Internet Services (LLM / Data Storage)
------------------------------------------------------------
CREATE TABLE InternetService (
    sid INT NOT NULL,
    provider VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    PRIMARY KEY (sid)
);

CREATE TABLE LLMService (
    sid INT NOT NULL,
    domain VARCHAR(100) NOT NULL,
    PRIMARY KEY (sid),
    CONSTRAINT fk_llmservice_is
        FOREIGN KEY (sid) REFERENCES InternetService(sid)
);

CREATE TABLE DataStorageService (
    sid INT NOT NULL,
    type VARCHAR(100) NOT NULL,
    PRIMARY KEY (sid),
    CONSTRAINT fk_dsservice_is
        FOREIGN KEY (sid) REFERENCES InternetService(sid)
);

------------------------------------------------------------
-- Q5: Relationship Tables
------------------------------------------------------------
CREATE TABLE Utilize (
    bmid INT NOT NULL,
    sid INT NOT NULL,
    version VARCHAR(50) NOT NULL,
    PRIMARY KEY (bmid, sid, version),
    CONSTRAINT fk_utilize_basemodel
        FOREIGN KEY (bmid) REFERENCES BaseModel(bmid)
        ON DELETE CASCADE,
    CONSTRAINT fk_utilize_internetservice
        FOREIGN KEY (sid) REFERENCES InternetService(sid)
        ON DELETE CASCADE
);

CREATE TABLE Configuration_Uses_CustomizedModel (
    cid INT NOT NULL,
    bmid INT NOT NULL,
    mid INT NOT NULL,
    duration_seconds INT NOT NULL,
    PRIMARY KEY (cid, bmid, mid),
    CONSTRAINT fk_cucm_configuration
        FOREIGN KEY (cid) REFERENCES Configuration(cid)
        ON DELETE CASCADE,
    CONSTRAINT fk_cucm_customizedmodel
        FOREIGN KEY (bmid, mid) REFERENCES CustomizedModel(bmid, mid)
        ON DELETE CASCADE
);

