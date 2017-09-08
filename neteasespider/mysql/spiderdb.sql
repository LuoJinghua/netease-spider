-- phpMyAdmin SQL Dump
-- version 4.2.7
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: 2017-09-08 08:02:09
-- 服务器版本： 10.0.27-MariaDB
-- PHP Version: 5.6.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `spiderdb`
--
CREATE DATABASE IF NOT EXISTS `spiderdb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `spiderdb`;

-- --------------------------------------------------------

--
-- 表的结构 `album_info`
--

CREATE TABLE IF NOT EXISTS `album_info` (
  `album_id` int(20) NOT NULL,
  `album_name` varchar(64) DEFAULT NULL,
  `album_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `artist_id` int(20) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `artist_info`
--

CREATE TABLE IF NOT EXISTS `artist_info` (
  `artist_id` int(20) NOT NULL DEFAULT '0',
  `artist_name` varchar(64) DEFAULT NULL,
  `gender` varchar(8) DEFAULT NULL,
  `category` varchar(32) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `music_info`
--

CREATE TABLE IF NOT EXISTS `music_info` (
  `music_id` int(20) NOT NULL,
  `music_name` varchar(64) DEFAULT NULL,
  `music_path` varchar(512) DEFAULT NULL,
  `artist_id` int(20) NOT NULL DEFAULT '0',
  `album_id` int(20) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `album_info`
--
ALTER TABLE `album_info`
 ADD PRIMARY KEY (`album_id`);

--
-- Indexes for table `artist_info`
--
ALTER TABLE `artist_info`
 ADD PRIMARY KEY (`artist_id`), ADD KEY `artist_name` (`artist_name`);

--
-- Indexes for table `music_info`
--
ALTER TABLE `music_info`
 ADD PRIMARY KEY (`music_id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
