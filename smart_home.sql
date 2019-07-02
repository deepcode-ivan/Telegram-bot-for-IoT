-- --------------------------------------------------------
-- Хост:                         127.0.0.1
-- Версия сервера:               10.2.10-MariaDB - mariadb.org binary distribution
-- Операционная система:         Win64
-- HeidiSQL Версия:              9.4.0.5125
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Дамп структуры базы данных smart_home
CREATE DATABASE IF NOT EXISTS `smart_home` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `smart_home`;

-- Дамп структуры для таблица smart_home.controllers
CREATE TABLE IF NOT EXISTS `controllers` (
  `controller_id` varchar(50) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `activation_code` varchar(50) DEFAULT NULL,
  `info` longtext DEFAULT NULL,
  PRIMARY KEY (`controller_id`),
  UNIQUE KEY `activation_code` (`activation_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Дамп данных таблицы smart_home.controllers: ~5 rows (приблизительно)
/*!40000 ALTER TABLE `controllers` DISABLE KEYS */;
REPLACE INTO `controllers` (`controller_id`, `created`, `activation_code`, `info`) VALUES
	('id_1', '2018-03-04 19:23:29', '1111', 'id_1 - модуль с набором сенсоров'),
	('id_2', '2018-03-11 21:28:31', '2222', 'id_2 - модуль с "умными" розетками'),
	('id_3', '2018-04-08 11:09:50', '3333', NULL),
	('id_4', '2018-04-08 11:11:49', '4444', NULL),
	('id_5', '2018-04-08 19:50:36', '5555', 'пятый модуль');
/*!40000 ALTER TABLE `controllers` ENABLE KEYS */;

-- Дамп структуры для таблица smart_home.device_data
CREATE TABLE IF NOT EXISTS `device_data` (
  `topic` varchar(50) NOT NULL,
  `controller_id` varchar(50) DEFAULT NULL,
  `topic_alias` varchar(50) DEFAULT NULL,
  `device_type` enum('SWITCH','SENSOR') DEFAULT NULL,
  `measurement` varchar(50) DEFAULT NULL,
  `value` varchar(50) DEFAULT 'no data',
  `climat_mode` enum('NONE','HEAT','COOL','METERING') DEFAULT 'NONE',
  `alarm_mode` bit(1) DEFAULT b'0',
  `updated` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`topic`),
  KEY `controller_id` (`controller_id`),
  CONSTRAINT `FK__controllers` FOREIGN KEY (`controller_id`) REFERENCES `controllers` (`controller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Дамп данных таблицы smart_home.device_data: ~12 rows (приблизительно)
/*!40000 ALTER TABLE `device_data` DISABLE KEYS */;
REPLACE INTO `device_data` (`topic`, `controller_id`, `topic_alias`, `device_type`, `measurement`, `value`, `climat_mode`, `alarm_mode`, `updated`) VALUES
	('id_1/door', 'id_1', 'входная дверь', 'SENSOR', 'состояние', 'Opened', 'NONE', b'0', '2018-06-02 09:57:23'),
	('id_1/hix', 'id_1', 'ощущаемая температура', 'SENSOR', 'градусы Цельсия', '22.50', 'NONE', b'0', '2018-06-01 00:11:49'),
	('id_1/hum', 'id_1', 'влажность', 'SENSOR', '%', '44.0', 'NONE', b'0', '2018-06-01 00:11:49'),
	('id_1/motion', 'id_1', 'Перемещения в пространстве', 'SENSOR', 'состояние', 'Motion detected', 'NONE', b'0', '2018-06-02 09:57:22'),
	('id_1/tem', 'id_1', 'температура', 'SENSOR', 'градусы Цельсия', '23.0', 'METERING', b'0', '2018-06-01 00:06:58'),
	('id_2/socket1', 'id_2', 'Обогреватель', 'SWITCH', 'состояние', '1', 'HEAT', b'0', '2018-06-02 09:57:47'),
	('id_2/socket2', 'id_2', 'Вентилятор', 'SWITCH', 'состояние', '0', 'COOL', b'0', '2018-05-31 23:57:33'),
	('id_2/socket3', 'id_2', 'Свет в зале', 'SWITCH', 'состояние', '0', 'NONE', b'0', '2018-06-02 09:57:09'),
	('id_2/socket4', 'id_2', 'Свет на кухне', 'SWITCH', 'состояние', '0', 'NONE', b'0', '2018-06-02 09:57:09'),
	('id_3/gas', 'id_3', 'утечка газа', 'SENSOR', 'состояние', '1', 'NONE', b'0', '2018-05-01 12:16:25'),
	('id_3/wather', 'id_3', 'утечка воды', 'SENSOR', 'состояние', 'no data', 'NONE', b'0', '2018-05-01 12:16:26'),
	('id_5/tem', 'id_5', 'температура на улице', 'SENSOR', 'градусы Цельсия', 'no data', 'NONE', b'0', '2018-04-22 19:45:06');
/*!40000 ALTER TABLE `device_data` ENABLE KEYS */;

-- Дамп структуры для таблица smart_home.users
CREATE TABLE IF NOT EXISTS `users` (
  `phone` varchar(50) NOT NULL,
  `telegram_id` varchar(50) DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Дамп данных таблицы smart_home.users: ~1 rows (приблизительно)
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
REPLACE INTO `users` (`phone`, `telegram_id`, `created`) VALUES
	('12345678900', NULL, '2018-05-19 19:48:39'),
	('79221440090', '431713612', '2018-05-24 22:21:52');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;

-- Дамп структуры для таблица smart_home.users_controllers
CREATE TABLE IF NOT EXISTS `users_controllers` (
  `phone` varchar(50) DEFAULT NULL,
  `controller_id` varchar(50) DEFAULT NULL,
  `root` bit(1) DEFAULT b'1',
  KEY `FK_users_controllers_users` (`phone`),
  KEY `FK_users_controllers_controllers` (`controller_id`),
  CONSTRAINT `FK_users_controllers_controllers` FOREIGN KEY (`controller_id`) REFERENCES `controllers` (`controller_id`),
  CONSTRAINT `FK_users_controllers_users` FOREIGN KEY (`phone`) REFERENCES `users` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Дамп данных таблицы smart_home.users_controllers: ~3 rows (приблизительно)
/*!40000 ALTER TABLE `users_controllers` DISABLE KEYS */;
REPLACE INTO `users_controllers` (`phone`, `controller_id`, `root`) VALUES
	('79221440090', 'id_1', b'1'),
	('12345678900', 'id_1', b'0'),
	('79221440090', 'id_2', b'1');
/*!40000 ALTER TABLE `users_controllers` ENABLE KEYS */;

-- Дамп структуры для таблица smart_home.voice_commands
CREATE TABLE IF NOT EXISTS `voice_commands` (
  `command_id` int(11) NOT NULL AUTO_INCREMENT,
  `topic` varchar(50) DEFAULT NULL,
  `command_text` text DEFAULT NULL,
  `command_type` enum('ON','OFF','DATA') DEFAULT NULL,
  PRIMARY KEY (`command_id`),
  KEY `FK_voice_commands_device_data` (`topic`),
  CONSTRAINT `FK_voice_commands_device_data` FOREIGN KEY (`topic`) REFERENCES `device_data` (`topic`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8;

-- Дамп данных таблицы smart_home.voice_commands: ~14 rows (приблизительно)
/*!40000 ALTER TABLE `voice_commands` DISABLE KEYS */;
REPLACE INTO `voice_commands` (`command_id`, `topic`, `command_text`, `command_type`) VALUES
	(5, 'id_1/tem', 'какая сейчас температура', 'DATA'),
	(13, 'id_5/tem', 'температура за окном', 'DATA'),
	(21, 'id_1/hum', 'какая сейчас влажность', 'DATA'),
	(22, 'id_2/socket1', 'включить обогреватель', 'ON'),
	(23, 'id_2/socket1', 'выключить обогреватель', 'OFF'),
	(24, 'id_2/socket2', 'включить вентилятор', 'ON'),
	(25, 'id_2/socket2', 'выключить вентилятор', 'OFF'),
	(27, 'id_2/socket3', 'включить свет в зале', 'ON'),
	(28, 'id_2/socket3', 'выключить свет в зале', 'OFF'),
	(29, 'id_2/socket3', 'включите свет в зале', 'ON'),
	(30, 'id_2/socket4', 'включить свет на кухне', 'ON'),
	(31, 'id_2/socket4', 'включите свет на кухне', 'ON'),
	(34, 'id_2/socket4', 'выключите свет на кухне', 'OFF'),
	(36, 'id_2/socket4', 'сделать на кухне светло', 'ON');
/*!40000 ALTER TABLE `voice_commands` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
