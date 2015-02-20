SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `fsodb` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
USE `fsodb` ;

-- -----------------------------------------------------
-- Table `fsodb`.`object`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `fsodb`.`object` ;

CREATE  TABLE IF NOT EXISTS `fsodb`.`object` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `path` TEXT NULL ,
  `manage` ENUM('manage','dontmanage','ignore') NULL ,
  `type` ENUM('file','directory','link') NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fsodb`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `fsodb`.`user` ;

CREATE  TABLE IF NOT EXISTS `fsodb`.`user` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `login` VARCHAR(255) NOT NULL ,
  `name` VARCHAR(255) NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `login_UNIQUE` (`login` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fsodb`.`object_log`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `fsodb`.`object_log` ;

CREATE  TABLE IF NOT EXISTS `fsodb`.`object_log` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `object_id` INT UNSIGNED NOT NULL ,
  `user_id` INT UNSIGNED NOT NULL ,
  `body` TEXT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_object_log_object_idx` (`object_id` ASC) ,
  INDEX `fk_object_log_user1_idx` (`user_id` ASC) ,
  CONSTRAINT `fk_object_log_object`
    FOREIGN KEY (`object_id` )
    REFERENCES `fsodb`.`object` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_object_log_user1`
    FOREIGN KEY (`user_id` )
    REFERENCES `fsodb`.`user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fsodb`.`platform`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `fsodb`.`platform` ;

CREATE  TABLE IF NOT EXISTS `fsodb`.`platform` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(100) NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fsodb`.`object_has_platform`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `fsodb`.`object_has_platform` ;

CREATE  TABLE IF NOT EXISTS `fsodb`.`object_has_platform` (
  `object_id` INT UNSIGNED NOT NULL ,
  `platform_id` INT UNSIGNED NOT NULL ,
  PRIMARY KEY (`object_id`, `platform_id`) ,
  INDEX `fk_object_has_platform_platform1_idx` (`platform_id` ASC) ,
  INDEX `fk_object_has_platform_object1_idx` (`object_id` ASC) ,
  CONSTRAINT `fk_object_has_platform_object1`
    FOREIGN KEY (`object_id` )
    REFERENCES `fsodb`.`object` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_object_has_platform_platform1`
    FOREIGN KEY (`platform_id` )
    REFERENCES `fsodb`.`platform` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
