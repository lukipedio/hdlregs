--------------------------------------------------------------------------------
-- HDLRegs adapter for Xilinx IPIF. 
--------------------------------------------------------------------------------
-- Copyright (c) 2013, Guy Eschemann
-- All rights reserved.
-- 
-- Redistribution and use in source and binary forms, with or without
-- modification, are permitted provided that the following conditions are met: 
-- 
-- 1. Redistributions of source code must retain the above copyright notice, this
--    list of conditions and the following disclaimer. 
-- 2. Redistributions in binary form must reproduce the above copyright notice,
--    this list of conditions and the following disclaimer in the documentation
--    and/or other materials provided with the distribution. 
-- 
-- THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
-- ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
-- WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
-- DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
-- ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
-- (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
-- LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
-- ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
-- (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
-- SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
-- 
-- The views and conclusions contained in the software and documentation are those
-- of the authors and should not be interpreted as representing official policies, 
-- either expressed or implied, of the FreeBSD Project.
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

entity ipif_adapter is
	port(
		-- IPIF interface
		Bus2IP_Clk    : in  std_logic;
		Bus2IP_Resetn : in  std_logic;
		Bus2IP_Addr   : in  std_logic_vector(31 downto 0);
		Bus2IP_RNW    : in  std_logic;
		Bus2IP_BE     : in  std_logic_vector(3 downto 0); -- not implemented yet
		Bus2IP_CS     : in  std_logic;
		Bus2IP_Data   : in  std_logic_vector(31 downto 0);
		IP2Bus_Data   : out std_logic_vector(31 downto 0);
		IP2Bus_WrAck  : out std_logic;
		IP2Bus_RdAck  : out std_logic;
		IP2Bus_Error  : out std_logic;
		-- register file interface
		regs_clk      : out std_logic;
		regs_rst      : out std_logic;
		regs_addr     : out std_logic_vector(31 downto 0);
		regs_cs       : out std_logic;
		regs_rnw      : out std_logic;
		regs_datain   : out std_logic_vector(31 downto 0);
		regs_dataout  : in  std_logic_vector(31 downto 0)
	);
end entity ipif_adapter;

architecture RTL of ipif_adapter is
begin
	regs_clk     <= Bus2IP_Clk;
	regs_rst     <= not Bus2IP_Resetn;
	regs_addr    <= Bus2IP_Addr;
	regs_cs      <= Bus2IP_CS;
	regs_rnw     <= Bus2IP_RNW;
	regs_datain  <= Bus2IP_Data;
	IP2Bus_Data  <= regs_dataout;
	IP2Bus_WrAck <= Bus2IP_CS and not Bus2IP_RNW;
	IP2Bus_RdAck <= Bus2IP_CS and Bus2IP_RNW;
	IP2Bus_Error <= '0';

end architecture RTL;
