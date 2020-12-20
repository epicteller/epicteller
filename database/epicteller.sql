DROP DATABASE IF EXISTS test_epicteller;
CREATE DATABASE IF NOT EXISTS test_epicteller;
USE test_epicteller;

CREATE TABLE IF NOT EXISTS `member`
(
    `id`        BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `url_token` VARCHAR(200)        NOT NULL,
    `name`      VARCHAR(50)         NOT NULL,
    `email`     VARCHAR(200)        NOT NULL,
    `passhash`  VARCHAR(100)        NOT NULL,
    `headline`  VARCHAR(1024)       NOT NULL DEFAULT '',
    `avatar`    VARCHAR(200)        NOT NULL DEFAULT '',
    `created`   BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `updated`   BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_url_token` (`url_token`),
    UNIQUE KEY `unq_email` (`email`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `member_external_id`
(
    `id`          BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `member_id`   BIGINT(20) UNSIGNED NOT NULL,
    `type`        TINYINT(4)          NOT NULL,
    `external_id` VARCHAR(200)        NOT NULL,
    `state`       TINYINT(4)          NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_member` (`member_id`),
    UNIQUE KEY `unq_member_type` (`member_id`, `type`),
    UNIQUE KEY `unq_type_external` (`type`, `external_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `room`
(
    `id`                  BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `url_token`           VARCHAR(200)        NOT NULL,
    `name`                VARCHAR(200)        NOT NULL,
    `description`         TEXT                NOT NULL,
    `owner_id`            BIGINT(20) UNSIGNED NOT NULL,
    `is_removed`          TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
    `current_campaign_id` BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `avatar`              VARCHAR(200)        NOT NULL DEFAULT '',
    `created`             BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `updated`             BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_url_token` (`url_token`),
    KEY `idx_owner_id` (`owner_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `room_running_episode`
(
    `id`         BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `room_id`    BIGINT(20) UNSIGNED NOT NULL,
    `episode_id` BIGINT(20) UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_room_id` (`room_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `room_member`
(
    `id`        BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `room_id`   BIGINT(20) UNSIGNED NOT NULL,
    `member_id` BIGINT(20) UNSIGNED NOT NULL,
    `created`   BIGINT(20) UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_room_member` (`room_id`, `member_id`),
    UNIQUE KEY `unq_member_room` (`member_id`, `room_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `room_external_id`
(
    `id`          BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `room_id`     BIGINT(20) UNSIGNED NOT NULL,
    `type`        TINYINT(4)          NOT NULL,
    `external_id` VARCHAR(200)        NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_room` (`room_id`),
    UNIQUE KEY `unq_room_type` (`room_id`, `type`),
    UNIQUE KEY `unq_type_external` (`type`, `external_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `campaign`
(
    `id`              BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `url_token`       VARCHAR(200)        NOT NULL,
    `room_id`         BIGINT(20)          NOT NULL,
    `name`            VARCHAR(200)        NOT NULL,
    `description`     TEXT                NOT NULL,
    `owner_id`        BIGINT(20) UNSIGNED NOT NULL,
    `state`           TINYINT(2)          NOT NULL DEFAULT 0,
    `is_removed`      TINYINT(1)          NOT NULL DEFAULT 0,
    `last_episode_id` BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `created`         BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `updated`         BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_url_token` (`url_token`),
    UNIQUE KEY `unq_room_name` (`room_id`, `name`),
    KEY `idx_room_id` (`room_id`),
    KEY `idx_owner_room_updated` (`owner_id`, `room_id`, `updated`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `character`
(
    `id`          BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `url_token`   VARCHAR(200)        NOT NULL,
    `member_id`   BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `campaign_id` BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `name`        VARCHAR(200)        NOT NULL,
    `avatar`      VARCHAR(200)        NOT NULL DEFAULT '',
    `description` TEXT                NOT NULL,
    `is_removed`  TINYINT(1)          NOT NULL DEFAULT 0,
    `data`        JSON                NOT NULL,
    `created`     BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `updated`     BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_url_token` (`url_token`),
    UNIQUE KEY `unq_campaign_name` (`campaign_id`, `name`),
    KEY `idx_name_campaign` (`name`, `campaign_id`),
    KEY `idx_member_id` (`member_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `character_external_id`
(
    `id`           BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `character_id` BIGINT(20) UNSIGNED NOT NULL,
    `type`         TINYINT(4)          NOT NULL,
    `external_id`  VARCHAR(200)        NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_character` (`character_id`),
    UNIQUE KEY `unq_character_type` (`character_id`, `type`),
    KEY `idx_type_external` (`type`, `external_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `episode`
(
    `id`          BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `url_token`   VARCHAR(200)        NOT NULL,
    `room_id`     BIGINT(20) UNSIGNED NOT NULL,
    `campaign_id` BIGINT(20) UNSIGNED NOT NULL,
    `title`       VARCHAR(200)        NOT NULL DEFAULT '',
    `state`       TINYINT(2)          NOT NULL DEFAULT 0,
    `is_removed`  TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
    `started_at`  BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `ended_at`    BIGINT(20) UNSIGNED          DEFAULT NULL,
    `created`     BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `updated`     BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_url_token` (`url_token`),
    KEY `idx_room_state` (`room_id`, `state`),
    KEY `idx_campaign` (`campaign_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `dice`
(
    `id`           BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `url_token`    VARCHAR(200)        NOT NULL,
    `character_id` BIGINT(20) UNSIGNED NOT NULL,
    `episode_id`   BIGINT(20) UNSIGNED NOT NULL,
    `type`         TINYINT(2)          NOT NULL DEFAULT 0,
    `expression`   TEXT                NOT NULL,
    `detail`       TEXT                NOT NULL,
    `reason`       TEXT                NOT NULL,
    `result`       JSON                NOT NULL,
    `created`      BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_url_token` (`url_token`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `message`
(
    `id`           BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `url_token`    VARCHAR(200)        NOT NULL,
    `episode_id`   BIGINT(20) UNSIGNED NOT NULL,
    `character_id` BIGINT(20) UNSIGNED NOT NULL,
    `type`         TINYINT(2)          NOT NULL DEFAULT 0,
    `is_removed`   TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
    `is_gm`        TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
    `content`      JSON                NOT NULL,
    `created`      BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    `updated`      BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_url_token` (`url_token`),
    KEY `idx_episode_id` (`episode_id`, `is_removed`, `id`),
    KEY `idx_character_id` (`character_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `combat_meta`
(
    `id`          BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `url_token`   VARCHAR(200)        NOT NULL,
    `campaign_id` BIGINT(20) UNSIGNED NOT NULL,
    `state`       TINYINT(2) UNSIGNED NOT NULL DEFAULT 0,
    `is_removed`  TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
    `data`        JSON                NOT NULL,
    `started_at`  BIGINT(20) UNSIGNED NOT NULL,
    `ended_at`    BIGINT(20) UNSIGNED NOT NULL,
    `created`     BIGINT(20) UNSIGNED NOT NULL,
    `updated`     BIGINT(20) UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unq_url_token` (`url_token`),
    KEY `idx_campaign_id` (`campaign_id`, `is_removed`, `id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;
