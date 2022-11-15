-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 15, 2022 at 01:12 PM
-- Server version: 10.4.25-MariaDB
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sencof_database`
--

-- --------------------------------------------------------

--
-- Table structure for table `category_coffee`
--

CREATE TABLE `category_coffee` (
  `CategoryID` int(12) NOT NULL,
  `nama_category` varchar(255) NOT NULL,
  `deskripsi_category` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `category_coffee`
--

INSERT INTO `category_coffee` (`CategoryID`, `nama_category`, `deskripsi_category`) VALUES
(2, 'Arabica', 'Pohon Kopi Arabika memiliki perakaran yang dangkal, Tanaman Kopi Arabika memiliki daun yang kecil,Buah Kopi Arabika lebih besar dibanding robusta.'),
(3, 'Arabica', 'Pohon Kopi Arabika memiliki perakaran yang dangkal, Tanaman Kopi Arabika memiliki daun yang kecil,Buah Kopi Arabika lebih besar dibanding robusta.');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `orderID` int(11) NOT NULL,
  `UserID` int(11) NOT NULL,
  `statusID` int(11) NOT NULL,
  `total_harga` int(11) NOT NULL,
  `waktu_order` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `order_detail`
--

CREATE TABLE `order_detail` (
  `id_order_detail` int(11) NOT NULL,
  `orderID` int(11) NOT NULL,
  `id_coffee` int(11) NOT NULL,
  `jumlah` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `id_coffee` int(12) NOT NULL,
  `CategoryID` int(12) NOT NULL,
  `nama_coffee` varchar(255) NOT NULL,
  `deskripsi_coffee` text NOT NULL,
  `stock` varchar(255) NOT NULL,
  `harga_per_kg` int(12) NOT NULL,
  `file_gambar_coffee` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `role`
--

CREATE TABLE `role` (
  `roleName` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `role`
--

INSERT INTO `role` (`roleName`) VALUES
('admin'),
('customer');

-- --------------------------------------------------------

--
-- Table structure for table `status`
--

CREATE TABLE `status` (
  `statusID` int(12) NOT NULL,
  `statusName` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `status`
--

INSERT INTO `status` (`statusID`, `statusName`) VALUES
(1, 'pending'),
(2, 'checkout'),
(3, 'canceled');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `userID` int(12) NOT NULL,
  `roleName` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `Time Stamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`userID`, `roleName`, `username`, `password`, `Time Stamp`) VALUES
(3, 'admin', 'admin', '$2b$12$t6KYCh1mZoKp7zzIvR4XTOiMjnSc2TALoVki2Jt7Fz.mzSzyFj1Fe', '2022-11-15 03:04:22'),
(4, 'admin', 'admin1', '$2b$12$zqXR5stxeKjq6E0XuDL8OuTVa8iYMyIuqW9E6dudDDdUOKYzGacVa', '2022-11-15 03:04:41'),
(5, 'admin', 'admin2', '$2b$12$sAc6KtLulrURv34RFsJeLecQxOxRbUJ0wSYNoc29/U2w.cWioTh7q', '2022-11-15 03:04:46'),
(6, 'customer', 'admin2', '$2b$12$YmgGDhe0rRJuaUyPJgTwyO8kQnbHQmhZpVRnZ061e1huiBloszF7a', '2022-11-15 06:51:10'),
(7, 'customer', 'admin2', '$2b$12$ssiMj68TSk1vPjrq/mi6dujaztf9r6u4aDKDYaCD3EKtvQdBRQMt.', '2022-11-15 07:10:55'),
(8, 'customer', 'pierro', '$2b$12$M52OR1Nh/UKWMgWB/vQtOOiJufDwYfQVBmkTeJE01b0V1Ji8J7ZKu', '2022-11-15 10:01:49');

-- --------------------------------------------------------

--
-- Table structure for table `user_info`
--

CREATE TABLE `user_info` (
  `infoID` int(12) NOT NULL,
  `userID` int(12) NOT NULL,
  `fullname` varchar(255) NOT NULL,
  `phone` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `city` varchar(255) NOT NULL,
  `zipcode` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `category_coffee`
--
ALTER TABLE `category_coffee`
  ADD PRIMARY KEY (`CategoryID`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`orderID`),
  ADD KEY `UserID` (`UserID`),
  ADD KEY `statusID` (`statusID`);

--
-- Indexes for table `order_detail`
--
ALTER TABLE `order_detail`
  ADD PRIMARY KEY (`id_order_detail`),
  ADD KEY `id_kopi` (`id_coffee`),
  ADD KEY `id_order` (`orderID`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`id_coffee`),
  ADD KEY `id_category_coffee` (`CategoryID`);

--
-- Indexes for table `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`roleName`);

--
-- Indexes for table `status`
--
ALTER TABLE `status`
  ADD PRIMARY KEY (`statusID`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`userID`),
  ADD KEY `roleName` (`roleName`);

--
-- Indexes for table `user_info`
--
ALTER TABLE `user_info`
  ADD PRIMARY KEY (`infoID`),
  ADD KEY `userID` (`userID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `userID` int(12) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `user` (`userID`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`statusID`) REFERENCES `status` (`statusID`);

--
-- Constraints for table `order_detail`
--
ALTER TABLE `order_detail`
  ADD CONSTRAINT `order_detail_ibfk_1` FOREIGN KEY (`id_coffee`) REFERENCES `product` (`id_coffee`),
  ADD CONSTRAINT `order_detail_ibfk_2` FOREIGN KEY (`orderID`) REFERENCES `orders` (`orderID`);

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`CategoryID`) REFERENCES `category_coffee` (`CategoryID`);

--
-- Constraints for table `user`
--
ALTER TABLE `user`
  ADD CONSTRAINT `user_ibfk_1` FOREIGN KEY (`roleName`) REFERENCES `role` (`roleName`);

--
-- Constraints for table `user_info`
--
ALTER TABLE `user_info`
  ADD CONSTRAINT `user_info_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `user` (`userID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
