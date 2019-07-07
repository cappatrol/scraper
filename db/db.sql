-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Jun 29, 2019 at 01:40 AM
-- Server version: 5.7.25
-- PHP Version: 7.3.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `ghin`
--

-- --------------------------------------------------------

--
-- Table structure for table `clubs`
--

CREATE TABLE `clubs` (
  `id` int(11) NOT NULL,
  `assn` varchar(255) NOT NULL,
  `club_number` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `clubs`
--

INSERT INTO `clubs` (`id`, `assn`, `club_number`, `password`) VALUES
(1, '11', '009', '20HPGCC13'),
(2, '55', '100', 'occ1903');

-- --------------------------------------------------------

--
-- Table structure for table `golfer`
--

CREATE TABLE `golfer` (
  `ghin_number` varchar(255) NOT NULL,
  `associationsnumber` varchar(255) DEFAULT NULL,
  `club_number` varchar(255) DEFAULT NULL,
  `sub_club_number` varchar(255) DEFAULT NULL,
  `club_name` varchar(255) DEFAULT NULL,
  `service_name` varchar(255) DEFAULT NULL,
  `hole` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `status_date` varchar(255) DEFAULT NULL,
  `_type` varchar(255) DEFAULT NULL,
  `p_name` varchar(255) DEFAULT NULL,
  `f_name` varchar(255) DEFAULT NULL,
  `m_name` varchar(255) DEFAULT NULL,
  `l_name` varchar(255) DEFAULT NULL,
  `s_l_name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `ref_url` varchar(255) DEFAULT NULL,
  `created_at` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `modified_at` varchar(255) DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `scraped_key` varchar(255) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `history`
--

CREATE TABLE `history` (
  `id` varchar(255) NOT NULL,
  `ghin_number` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `index` varchar(255) DEFAULT NULL,
  `tscores` varchar(255) DEFAULT NULL,
  `ref_url` varchar(255) DEFAULT NULL,
  `created_at` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `modified_at` varchar(255) DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `scraped_key` varchar(255) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `score`
--


CREATE TABLE `score` (
  `id` varchar(255) NOT NULL,
  `ghin_number` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `score` varchar(255) DEFAULT NULL,
  `cr_slope` varchar(255) DEFAULT NULL,
  `used` varchar(255) DEFAULT NULL,
  `diff` varchar(255) DEFAULT NULL,
  `course` varchar(255) DEFAULT NULL,
  `date_update` varchar(255) DEFAULT NULL,
  `ref_url` varchar(255) DEFAULT NULL,
  `created_at` varchar(255) DEFAULT NULL,
  `created_by` varchar(255) DEFAULT NULL,
  `modified_at` varchar(255) DEFAULT NULL,
  `modified_by` varchar(255) DEFAULT NULL,
  `scraped_key` varchar(255) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `clubs`
--
ALTER TABLE `clubs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `golfer`
--
ALTER TABLE `golfer`
  ADD PRIMARY KEY (`ghin_number`);

--
-- Indexes for table `history`
--
ALTER TABLE `history`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `score`
--
ALTER TABLE `score`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `clubs`
--
ALTER TABLE `clubs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
