use master
go

CREATE DATABASE Northwind1


use Northwind1 
go

-- 14 Phân mảnh dọc trên bảng Employee 
-- Phân mảnh nhân viên gồm có 4 cột: Employee, LastName, FirstName, TitleOfCourtesy
-- Phân mảnh NV2 gồm các cột còn lại và cột employee ID

SELECT E.EmployeeID, E.LastName, E.FirstName, E.TitleOfCourtesy INTO Northwind1.dbo.NV1
FROM Northwind.dbo.Employees as E


SELECT E.EmployeeID, E.Title, E.BirthDate, E.HireDate, E.Address, E.Region, E.PostalCode, E.Country, E.HomePhone, E.Extension, E.Photo, E.PhotoPath, E.ReportsTo, E.Notes 
INTO Northwind1.dbo.NV2
FROM Northwind.dbo.Employees as E


-- 15 . Danh sách tất cả nhân viên mức 1: 

SELECT * FROM Northwind.dbo.Employees

-- 16 Danh sách tất cả sinh viên ở mức 2

SELECT E2.*, E1.FirstName, E1.LastName, E1.TitleOfCourtesy
FROM Northwind1.dbo.NV1 as E1, Northwind1.dbo.NV2 as E2
Where E1.EmployeeID = E2.EmployeeID


-- ===========================================================================================
-- =============== Bai TH5 ===================================================================
-- ===========================================================================================


--- 1. Chuột phải vào Databases chọn restore Database, phần device chọn file đuôi bak để restore, sau đó nhấn oke
use Northwind1
go
--- 2. Tạo View để thống kê số lượng khách hàng của từng quốc gia của khách hàng đã mua ở 2 

--- Mức 1: ViewThongKeSLKHTheoQGMuc1 trên Northwind
CREATE VIEW ViewThongKeSLKHTheoQGMuc1 AS
SELECT C.Country, COUNT(C.CustomerID) as SoLuongKH
FROM Northwind.dbo.Customers as C
GROUP BY C.Country

SELECT * From ViewThongKeSLKHTheoQGMuc1
--- Mức 2: ViewThongKeSLKHTheoQGMuc2 trên Northwind1
CREATE VIEW ViewThongKeSLKHTheoQGMuc2 AS
SELECT Country, COUNT(CustomerID) as SoLuongKH
FROM Northwind1.dbo.KH1
GROUP BY Country
UNION
SELECT Country, COUNT(CustomerID) as SoLuongKH
FROM Northwind1.dbo.KH2
GROUP BY Country

SELECT * FROM ViewThongKeSLKHTheoQGMuc2

-- 3. Tạo view số lượng đơn hàng từng quốc gia theo cột quốc gia và số lượng

--- Mức 1: ViewThongKeSLDHTheoQGMuc1 trên Northwind
CREATE VIEW ViewThongKeSLDHTheoQGMuc1 AS
SELECT c.Country, COUNT(o.OrderID) as SoLuong
FROM Northwind.dbo.Customers as c, Northwind.dbo.Orders as o
WHERE c.CustomerID = o.CustomerID
GROUP BY c.Country

SELECT * FROM ViewThongKeSLDHTheoQGMuc1 ORDER BY SoLuong


--- Mức 2: ViewThongKeSLDHTheoQGMuc2 trên Northwind1
CREATE VIEW ViewThongKeSLDHTheoQGMuc2 AS
SELECT c.Country, COUNT(o.OrderID) as SoLuong
FROM Northwind1.dbo.KH1 as c, Northwind.dbo.Orders as o
WHERE c.CustomerID = o.CustomerID
GROUP BY c.Country
UNION
SELECT c.Country, COUNT(o.OrderID) as SoLuong
FROM Northwind1.dbo.KH2 as c, Northwind.dbo.Orders as o
WHERE c.CustomerID = o.CustomerID
GROUP BY c.Country

SELECT * FROM ViewThongKeSLDHTheoQGMuc2 ORDER BY SoLuong


--- 4. Tạo Procedure để in ra danh sách KH chưa mua đơn nào

-- MỨC 1: ProcKHChuaMuaHangMuc1 trên trên Northwind

CREATE PROC ProcKHChuaMuaHangMuc1
AS
SELECT *
FROM Northwind.dbo.Customers
WHERE CustomerID not in (
	SELECT DISTINCT CustomerID
	FROM Northwind.dbo.Orders
)
GO

exec ProcKHChuaMuaHangMuc1

DROP PROC ProcKHChuaMuaHangMuc1

-- Mức 2: ProcKHChuaMuaHangMuc2 trên trên Northwind1

CREATE PROC ProcKHChuaMuaHangMuc2
AS
BEGIN
	SELECT *
	FROM Northwind1.dbo.KH1
	WHERE CustomerID not in (
	SELECT DISTINCT CustomerID
	FROM Northwind.dbo.Orders
	)
	UNION
	SELECT *
	FROM Northwind1.dbo.KH2
	WHERE CustomerID not in (
	SELECT DISTINCT CustomerID
	FROM Northwind.dbo.Orders
	)
END
GO

-- XEM lại dữ liệu

EXEC ProcKHChuaMuaHangMuc2
GO
-- Xóa PROC
DROP PROC ProcKHChuaMuaHangMuc2
GO

-- 5. TẠo PROC để thêm dữ liệu KH: CustomerID, CompanyName, City, Country

-- MỨC 1: - ProcThemKHMuc1 trên trên Northwind

CREATE PROC ProcThemKHMuc1 (@id nvarchar(5), @company nvarchar(40), @city nvarchar(15), @country nvarchar(15))
AS
BEGIN
	INSERT INTO Northwind.dbo.Customers (CustomerID, CompanyName, City, Country) Values (@id,@company,@city,@country)
END
GO

-- Test
EXEC ProcThemKHMuc1 N'LN123', N'Officience', N'Hồ Chí Minh', N'Việt Nam'
EXEC ProcThemKHMuc1 N'KH001', N'Công ty 001', N'HCMC', N'Vietnam'
EXEC ProcThemKHMuc1 N'KH002', N'Công ty 002', N'London', N'UK'
-- Xem lại

SELECT * FROM Northwind.dbo.Customers WHERE CustomerID=N'LN123'
GO
SELECT * FROM Northwind.dbo.Customers WHERE CustomerID=N'KH001'

DROP PROC ProcThemKHMuc1

-- Mức 2: ProcThemKHMuc2 trên trên Northwind1

CREATE PROC ProcThemKHMuc2 (@id nvarchar(5), @company nvarchar(40), @city nvarchar(15), @country nvarchar(15))
AS
BEGIN
	if (@country in (N'USA',N'UK'))
		INSERT INTO Northwind1.dbo.KH1 (CustomerID, CompanyName, City, Country) Values (@id,@company,@city,@country)
	else
		INSERT INTO Northwind1.dbo.KH2 (CustomerID, CompanyName, City, Country) Values (@id,@company,@city,@country)
END
GO

-- TEst 
EXEC ProcThemKHMuc2 N'LN123', N'Officience', N'Hồ Chí Minh', N'Việt Nam'
EXEC ProcThemKHMuc2 N'KH001', N'Công ty 001', N'HCMC', N'Vietnam'
-- Xem lại

SELECT * FROM Northwind1.dbo.KH2 WHERE CustomerID=N'KH001'
GO

-- TEst 
EXEC ProcThemKHMuc2 N'KH002', N'Công ty 002', N'London', N'UK'

-- Xem lại

SELECT * FROM Northwind1.dbo.KH1 WHERE CustomerID=N'KH002'
GO

-- 6. Tạo PROC sửa dữ liệu về địa điểm công ty khách hàng

-- Mức 1: ProcSuaKHMuc1

CREATE PROC ProcSuaKHMuc1 (@id nvarchar(5), @city nvarchar(15), @country nvarchar(15))
AS
BEGIN
UPDATE Northwind.dbo.Customers
SET City=@city, Country=@country
WHERE CustomerID = @id
END
GO

--  TEST
EXEC ProcSuaKHMuc1 N'KH001', N'San Francisco', N'USA'
GO

-- view
SELECT * FROM Northwind.dbo.Customers WHERE CustomerID=N'KH001'
Go

EXEC ProcSuaKHMuc1 N'KH002', N'HANOI',N'Vietnam'
GO

SELECT * FROM Northwind.dbo.Customers WHERE CustomerID=N'KH002'
Go

---- Mức 2: ProcSuaKHMuc2 trên trên Northwind1

CREATE PROC ProcSuaKHMuc2 (@id nvarchar(5), @city nvarchar(15), @country nvarchar(15))
AS
BEGIN
	
		UPDATE Northwind1.dbo.KH1
		SET City=@city, Country=@country
		WHERE CustomerID = @id


		UPDATE Northwind1.dbo.KH2
		SET City=@city, Country=@country
		WHERE CustomerID = @id
	
END
GO


EXEC ProcSuaKHMuc2 N'KH001', N'San Francisco', N'USA'
EXEC ProcSuaKHMuc2 N'KH002', N'HANOI', N'Vietnam'

SELECT * FROM Northwind1.dbo.KH1 WHERE CustomerID in ( N'KH001', N'KH002')
UNION
SELECT * FROM Northwind1.dbo.KH2 WHERE CustomerID in ( N'KH001', N'KH002')


-- 7. Tạo proc để xóa dữ liệu kh

-- MỨC 1: ProcXoaKHMuc1 trên trên Northwind

CREATE PROC ProcXoaKHMuc1 (@id nvarchar(5))
AS
BEGIN
	DELETE Northwind.dbo.Customers WHERE CustomerID = @id
END
GO

EXEC ProcXoaKHMuc1 N'KH001'
EXEC ProcXoaKHMuc1 N'KH002'

-- MỨC 2: ProcXoaKHMuc2 trên trên Northwind

CREATE PROC ProcXoaKHMuc2 (@id nvarchar(5))
AS
BEGIN
	DELETE Northwind1.dbo.KH1 WHERE CustomerID = @id
	DELETE Northwind1.dbo.KH2 WHERE CustomerID = @id
END
GO

EXEC ProcXoaKHMuc2 N'KH001'
EXEC ProcXoaKHMuc2 N'KH002'

--- 9. Tạo FUNC tính danh sách đơn 