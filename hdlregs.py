#!/usr/bin/python

# Copyright (c) 2013, Guy Eschemann
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.

import re
import sys
import json
import datetime
from string import Template

# ------------------------------------------------------------------------------
# Constants
#

HDLREGS_VERSION = "0.2"

INDENTATION_WIDTH = 4

RESERVED_VHDL_KEYWORDS = ("abs", "access", "after", "alias", "all", "and", "architecture", "array", "assert", "attribute", "begin", "block", "body", "buffer", "bus", "case", "component", "configuration", "constant", "disconnect", "downto", "else", "elsif", "end", "entity", "exit", "file", "for", "function", "generate", "generic", "group", "guarded", "if", "impure", "in", "inertial", "inout", "is", "label", "library", "linkage", "literal", "loop", "map", "mod", "nand", "new", "next", "nor", "not", "null", "of", "on", "open", "or", "others", "out", "package", "port", "postponed", "procedure", "process", "pure", "range", "record", "register", "reject", "rem", "report", "return", "rol", "ror", "select", "severity", "signal", "shared", "sla", "sll", "sra", "srl", "subtype", "then", "to", "transport", "type", "unaffected", "units", "until", "use", "variable", "wait", "when", "while", "with", "xnor", "xor")

RESERVED_C_KEYWORDS  = ("auto", "else", "long", "switch", "break", "enum", "register", "typedef", "case", "extern", "return", "union", "char", "float", "short", "unsigned", "const", "for", "signed", "void", "continue", "goto", "sizeof", "volatile", "default", "if", "static", "while", "do", "int", "struct", "_Packed", "double")

# ------------------------------------------------------------------------------
# String templates for C, VHDL and HTML documents
#

HTML_DOC_TEMPLATE = Template("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Registers in '$module_name' module</title>
    <style type="text/css" media="screen,print">

    body, html{
        margin:0;
        padding:0;    
        font-family:Verdana,Geneva,Arial,sans-serif;        
        font-size: small;
    }

    h1 {
        margin:0;
    }

    /* registers table */
    table.register { 
        border: thin solid #aaa; 
        border-collapse: collapse;
        border-spacing:0;
        }    
    table.register tr.Header{
        background-color: #edf0f9;
        height: 2em;
        font-size: 125%;
        }
    table.register td.RegisterAddr {
        width: 10em; 
        text-align: left; 
        font-weight: bold; 
        padding: 5px;
        }
    table.register td.RegisterName {
        font-weight: bold; 
        padding: 5px;  
        }
    table.register td.RegisterDescription {
        border-bottom: thin solid #aaa; 
        padding: 5px; 
        padding-top: 0; 
        background-color: #edf0f9;
        }
    table.register td.BitFieldIndex {
        padding-right: 1em; 
        padding-top: 3px; 
        width: 5em; text-align: right; 
        vertical-align: top; 
        border-top: thin solid #aaa; 
        }
    table.register td.BitFieldName {
        width: 25em; 
        text-align: left; 
        border-top: thin solid #aaa; 
        font-weight: bold; 
        }
    table.register td.BitFieldMode {
        width: 3em; 
        text-align: left; 
        border-top: thin solid #aaa; 
        }
    table.register td.BitFieldReset {
        text-align: left;
        vertical-align: top; 
        border-top: thin solid #aaa; 
        }  
        
    /* overview table format */
    table#overview{
        width: 200px;
        border: none;
    }    
    table#overview tr {
        height: 1.5em;
    }        
    table#overview td {
        padding-left: 1em;
    }        
    .even{
        background-color: #eee;
    }
    a.overview {
        color: black;
        text-decoration: none;
    }    
        
    #footer p {
        margin:0;
    }
    
    #sidebar ul {
        margin:0;
        padding:0;
        list-style:none;
    }    
    
    div#wrap {
        width:750px;
        margin:1em auto;
        border: solid 2px #aaa;
        padding: 5px;
        -webkit-border-radius: 10px;
        -moz-border-radius: 10px;
        -o-border-radius: 10px;
        -ms-border-radius: 10px;
        -khtml-border-radius: 10px;
        border-radius: 3px;        
        
    }    
    
    div#header {
        padding:10px 10px;
        /*border-width: 0 0 0.1em 0;*/
        /*border-style: double;*/
        border-color: #aaa;        
    }        
    
    div#footer {
        clear:both; /*push footer down*/
        padding:5px 10px;
        text-align:center;
        border-width: 0.1em 0 0 0;
        border-style: double;
        border-color: #aaa;        
        font-size: x-small;
        
    }        

    div#sidebar {
        width:200px; /* subtract padding from actual width*/
        float:left;
        padding:10px;        
    }    
    
    div#main {
        width: 510px; /* subtract padding from actual width*/
        float:right;
        padding:10px;
    }        
    
    </style>
    
</head>
<body>

    <div id="wrap">

        <div id="header">
            <h1>Registers in '$module_name' module</h1>
        </div>

        <div id="sidebar">
            <h2>Overview</h2>
$overview
        </div>
        
        <div id="main">
            <h2>Detailed description</h2>
            $registers           
        </div>
        
        <div id="footer">
        <p>Generated: $date_time by <a href="https://github.com/noasic/hdlregs">HDLRegs</a> version $hdlregs_version</p>
        </div>
    </div>

</body>
</html>""")    

# ------------------------------------------------------------------------------

HTML_REGISTER_TEMPLATE = Template("""    
  <p>
  <a id="$register_name"></a>
  <table class="register">
    <tr class="Header">
      <td class="RegisterName" colspan="3">$register_name</td>    
      <td class="RegisterAddr">$register_addr_offset</td>          
    </tr>
    <tr>
      <td class="RegisterDescription" colspan="4">$register_description</td>          
    </tr>
    $register_fields   
  </table>
  </p>""")  # html_register_template

# ------------------------------------------------------------------------------

HTML_REGISTER_FIELD_TEMPLATE = Template("""
    <tr class="BitField">
      <td class="BitFieldIndex" rowspan="2">[$field_range]</td>
      <td class="BitFieldName">$field_name</td>
      <td class="BitFieldMode">$field_access</td>
      <td class="BitFieldReset">Reset: $field_reset</td>            
    </tr>
    <tr>
      <td class="BitFieldDescription">$field_description</td>
      <td>&nbsp;</td>
      <td class="BitFieldExtReset">
      </td>
    </tr>  
""")  # html_register_field_template

# ------------------------------------------------------------------------------

c_header_template = Template("""
// Header for module '${json_module_name}'
// automatically generated by HDLRegs version $hdlregs_version on $date_time

#ifndef ${module_name}_H
#define ${module_name}_H

//
// Register address offsets
//
$address_offsets
$fields
#endif // ${module_name}_H
""")

# ------------------------------------------------------------------------------

vhdl_package_template = Template("""
-- VHDL package for module '${json_module_name}'
-- automatically generated by HDLRegs version $hdlregs_version on $date_time

library ieee;
use ieee.std_logic_1164.all;
package $package_name is
$declarations
end package $package_name;
""")

# ------------------------------------------------------------------------------

vhdl_component_template = Template("""
-- VHDL component for module '${json_module_name}'
-- automatically generated by HDLRegs version $hdlregs_version on $date_time

library ieee;

use ieee.std_logic_1164.all;
use work.$package_name.all;

entity $entity_name is
    port(
        clk     : in  std_logic;                     -- system clock
        rst     : in  std_logic;                     -- synchronous, high-active
        addr    : in  std_logic_vector(31 downto 0); -- read/write address
        cs      : in  std_logic;                     -- chip select
        rnw     : in  std_logic;                     -- read (1) or write (0)
        datain  : in  std_logic_vector(31 downto 0); -- write data
        dataout : out std_logic_vector(31 downto 0); -- read data
        --
        regs2user : out t_regs2user; -- register file -> user logic
        user2regs : in t_user2regs -- user logic -> register file
    );
end entity $entity_name;

architecture RTL of $entity_name is
$signal_declarations
begin
$register_write_proc
$register_read_proc
$concurrent_signal_assignments
end architecture RTL;

""")

# ------------------------------------------------------------------------------
# VHDL code blocks
#

class VhdlRecord:
    #
    def __init__(self, name, description, elements):
        self.name = name
        self.description = description
        self.elements_ = elements
    #
    def add_element(self, element):
        self.elements_.append(element)
    #
    def __str__(self):
        raise NotImplementedError
    #
    def to_str(self, level):
        str = '\n'
        str += indent(level) + "-- %s\n" % self.description
        str += indent(level) + "type %s is record\n" % self.name
        level += 1
        for e in self.elements_:
            str += indent(level) + e + ";\n"
        level -= 1
        str += indent(level) + "end record;\n"
        return str
    #
    def name(self):
        return self.name
    #
    # Returns the number elements within the record
    def num_elements(self):
        return len(self.elements_)
    
class VhdlPackage:
    #
    def __init__(self, name):
        self.name = name
        self.declarations_ = []
    #
    def add_declaration(self, declaration):
        self.declarations_.append(declaration)
    #
    def __str__(self):
        str_declarations = ''
        for d in self.declarations_:
            str_declarations += d.to_str(1)
        d = dict(package_name = self.name, 
                 declarations = str_declarations,
                 json_module_name = module.name,
                 hdlregs_version = HDLREGS_VERSION,
                 date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        return vhdl_package_template.substitute(d)

class VhdlIfStatement:
    #
    def __init__(self, condition):
        self._condition = condition
        self.statements = []
    #
    def to_str(self, level):
        str = indent(level) + 'if %s then\n' % self._condition
        level += 1
        for s in self.statements:
            str += "%s" % s.to_str(level)
        level -= 1
        str += indent(level) + 'end if;\n'
        return str
    #   
    def __str__(self):
        raise NotImplementedError

class VhdlClockedProcess:
    #
    def __init__(self, name, clock, reset):
        self.name = name
        self.clock = clock
        self.reset = reset
        self.reset_statements = []
        self.statements = []
    #
    def to_str(self, level):
        s = indent(level) + '%s : process(%s) is\n' % (self.name, self.clock)
        s += indent(level) + 'begin\n'
        level += 1
        s += indent(level) + "if rising_edge(%s) then\n" % self.clock
        level += 1
        s += indent(level) + "if %s = '1' then\n" % self.reset
        level += 1
        for st in self.reset_statements:
            s += "%s" % st.to_str(level)
        level -= 1
        s += indent(level) + "else\n"
        level += 1 
        for st in self.statements:            
            s += st.to_str(level)
        level -= 1
        s += indent(level) + "end if;\n"
        level -= 1        
        s += indent(level) + "end if;\n"
        level -= 1        
        s += indent(level) + 'end process %s;\n' % self.name
        return s
    #   
    def __str__(self):
        raise NotImplementedError
    
class VhdlAsyncProcess():
    #
    def __init__(self, name):
        self.name = name
        self.sensitivity = []
        self.statements = []        
    #
    def to_str(self, level):
        if len(self.sensitivity) > 0:
             sensitivity = "(%s)" % (','.join(self.sensitivity))
        else:
             sensitivity = ''        
        s = indent(level) + '%s : process %s is\n' % (self.name, sensitivity)
        s += indent(level) + 'begin\n'
        level += 1
        for st in self.statements:            
            s += st.to_str(level)
        level -= 1
        s += indent(level) + 'end process %s;\n' % self.name
        return s
    #
    def __str__(self):
        raise NotImplementedError
        
class VhdlCodeBlock():
    #
    def __init__(self):
        self.statements = []
    #
    def to_str(self, level):
        s = '\n'
        for st in self.statements:
            s += st.to_str(level)
        return s    
    #
    def __str__(self):
        raise NotImplementedError
        
class VhdlStatement():
    #
    def __init__(self, value):
        self._value = value
    #
    def to_str(self, level):
        return indent(level) + self._value
    #
    def __str__(self):
        raise NotImplementedError

class VhdlDeclaration():
    #
    def __init__(self, value):
        self._value = value
    #
    def to_str(self, level):
        return indent(level) + self._value
    #
    def __str__(self):
        raise NotImplementedError
        
# ------------------------------------------------------------------------------
# Code generators
#

#
# The mother of all code generators
#
class CodeGenerator():    
    #
    # Returns a field's bit width identifier, e.g. 'WIDTH_CONTROL_RESET'
    def bitWidth_identifier(self, field):
        return 'WIDTH_' + field.parent_reg.name.upper() + '_' + field.name.upper()
    #
    # Returns a field's bit offset identifier, e.g. 'OFFSET_CONTROL_RESET'
    def bitOffset_identifier(self, field):
        return 'OFFSET_' + field.parent_reg.name.upper() + '_' + field.name.upper()
    #
    # Returns a field's bit mask identifier, e.g. 'MASK_CONTROL_RESET'
    def bitMask_identifier(self, field):
        return 'MASK_' + field.parent_reg.name.upper() + '_' + field.name.upper()
    #
    # Returns the name of the record type corresponding to this field
    def vhdl_record_name(self, field):        
        return 't_' + field.parent_reg.name.lower() + '_' + field.name.lower()
    #
    # Returns the name of the VHDL package for a module
    def vhdl_package_name(self, module):
        return module.name.lower() + '_regs_pkg'      
    #
    # Return a register's address identifier, e.g. 'ADDR_CONTROL'
    def address_identifier(self, register):
        return "ADDR_" + register.name.upper()
    #
    # Get a registers's data signal name    
    def vhdl_data_signal(self, register):
        return 's_' + register.name.lower() + "_r"    
    #
    # Get a registers's strobe signal name    
    def vhdl_strobe_signal(self, register):
        return 's_' + register.name.lower() + "_strobe_r"    
    #
    # Returns the name of the VHDL entity for a module
    def vhdl_entity_name(self, module):
        return module.name.lower() + '_regs'      
       
#
# VHDL component generator
#
class VhdlComponentGenerator(CodeGenerator):
    def __init__(self, module):
        #
        # Signal declarations
        signal_declarations = VhdlCodeBlock()
        for r in module.registers:
            signal_declarations.statements.append(VhdlStatement('signal %s : std_logic_vector(31 downto 0) := x"%.8X";\n' % (self.vhdl_data_signal(r), r.reset())))
            if r.is_bus_writable():
                signal_declarations.statements.append(VhdlStatement("signal %s : std_logic := '0';\n" % (self.vhdl_strobe_signal(r))))
        
        #
        # Register-write process
        register_write_proc = VhdlClockedProcess("register_write", "clk", "rst")
        # resets
        for r in module.registers:
            register_write_proc.reset_statements.append(VhdlStatement('%s <= x"%.8X";\n' % (self.vhdl_data_signal(r), r.reset())))
        # defaults
        register_write_proc.statements.append(VhdlStatement("-- defaults:\n"))
        for r in module.registers:
            if r.is_bus_writable():
                register_write_proc.statements.append(VhdlStatement("%s <= '0';\n" % self.vhdl_strobe_signal(r)))
        # bus-write
        register_write_proc.statements.append(VhdlStatement("-- bus write:\n"))
        bus_write_block = VhdlIfStatement("cs = '1' and rnw = '0'")
        for r in module.registers:
            reg_data_signal = self.vhdl_data_signal(r)
            reg_strobe_signal = self.vhdl_strobe_signal(r)
            if r.is_bus_writable():
                register_write_block = VhdlIfStatement("addr = %s" % self.address_identifier(r))
                for f in r.fields:
                    if f.is_bus_writable():
                        index_high = "%s + %s - 1" % (self.bitOffset_identifier(f), self.bitWidth_identifier(f))
                        index_low = self.bitOffset_identifier(f)
                        register_write_block.statements.append(VhdlStatement("%s(%s downto %s) <= datain(%s downto %s);\n" % (reg_data_signal, index_high, index_low, index_high, index_low)))
                        register_write_block.statements.append(VhdlStatement("%s <= '1';\n" % (reg_strobe_signal)))
                bus_write_block.statements.append(register_write_block)
        register_write_proc.statements.append(bus_write_block)
        # user-logic write
        register_write_proc.statements.append(VhdlStatement("-- user-logic write:\n"))        
        for r in module.registers:
            for f in r.fields:
                if f.is_user_writable():
                    field_write_block = VhdlIfStatement("user2regs.%s.%s.strobe = '1'" % (r.name, f.name))
                    field_write_block.statements.append(VhdlStatement("%s(%s + %s - 1 downto %s) <= user2regs.%s.%s.value;\n" % (self.vhdl_data_signal(r), self.bitOffset_identifier(f), self.bitWidth_identifier(f), self.bitOffset_identifier(f), r.name, f.name)))
                    register_write_proc.statements.append(field_write_block)
        #
        # Bus-read process
        bus_read_proc = VhdlAsyncProcess("bus_read")
        bus_read_proc.sensitivity.append('cs')
        bus_read_proc.sensitivity.append('rnw')
        bus_read_proc.sensitivity.append('addr')
        bus_read_proc.statements.append(VhdlStatement("dataout <= (others => 'X'); -- default\n"))
        cs_block = VhdlIfStatement("cs = '1' and rnw = '1'")
        for r in module.registers:
            if r.is_bus_readable():
                bus_read_proc.sensitivity.append(self.vhdl_data_signal(r))
                reg_read_block = VhdlIfStatement("addr = %s" % self.address_identifier(r))
                for f in r.fields:
                    if f.is_bus_readable():
                        index_high = "%s + %s - 1" % (self.bitOffset_identifier(f), self.bitWidth_identifier(f))
                        index_low = self.bitOffset_identifier(f)
                        reg_read_block.statements.append(VhdlStatement("dataout(%s downto %s) <= %s(%s downto %s);\n" % (index_high, index_low, self.vhdl_data_signal(r), index_high, index_low)))
                cs_block.statements.append(reg_read_block)                
        bus_read_proc.statements.append(cs_block)
        #
        # Concurrent signal assignments
        concurrent_signal_assignments = VhdlCodeBlock()
        for r in module.registers:
            for f in r.fields:
                if f.is_bus_writable():
                    concurrent_signal_assignments.statements.append(VhdlStatement("regs2user.%s.%s.value <= %s(%s + %s - 1 downto %s);\n" % (r.name, f.name, self.vhdl_data_signal(r), self.bitOffset_identifier(f), self.bitWidth_identifier(f), self.bitOffset_identifier(f))))
                    concurrent_signal_assignments.statements.append(VhdlStatement("regs2user.%s.%s.strobe <= %s;\n" % (r.name, f.name, self.vhdl_strobe_signal(r))))                   
        d = dict(entity_name = self.vhdl_entity_name(module),
                 signal_declarations = signal_declarations.to_str(1),
                 package_name = self.vhdl_package_name(module),
                 register_write_proc = register_write_proc.to_str(1),
                 concurrent_signal_assignments = concurrent_signal_assignments.to_str(1),
                 register_read_proc = bus_read_proc.to_str(1),
                 json_module_name = module.name,
                 hdlregs_version = HDLREGS_VERSION,
                 date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self._code = vhdl_component_template.substitute(d)        
    #
    # Save the generated VHDL component to a file
    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(self._code)    

#
# VHDL package generator
#
class VhdlPackageGenerator(CodeGenerator):
    def __init__(self, module):
        vhdl_package = VhdlPackage(self.vhdl_package_name(module))
        # Interface record types     
        user2regs = VhdlRecord('t_user2regs', 'User-logic -> register file interface', [])
        regs2user = VhdlRecord('t_regs2user', 'Register file -> user-logic interface', [])
        # Register address offsets
        for r in module.registers:
            vhdl_package.add_declaration(VhdlDeclaration('constant %s : std_logic_vector(31 downto 0) := x"%.8X";\n' % (self.address_identifier(r), r.addressOffset)))
        # Field constants:
        for r in module.registers:
            for f in r.fields:
                vhdl_package.add_declaration(self.to_vhdl_constants(f))
        # Field record types
        field_types = ''
        for r in module.registers:
            for f in r.fields:
                description = "Field '%s' of register '%s' (%s)" % (f.name, r.name, f.access())
                elements = []
                elements.append("value : std_logic_vector(%s - 1 downto 0)" % (self.bitWidth_identifier(f)))
                elements.append("strobe : std_logic")
                record = VhdlRecord(self.vhdl_record_name(f), description, elements)
                vhdl_package.add_declaration(record)       
        # Register record types (XXX_regs2user and/or XXX_user2regs)
        for r in module.registers:
            records = self.to_vhdl_records(r)
            for record in records:
                if record.name.endswith('user2regs'):
                    user2regs.add_element(r.name + ": " + record.name)
                if record.name.endswith('regs2user'):
                    regs2user.add_element(r.name + ": " + record.name)
                vhdl_package.add_declaration(record)
        # Add dummy signals in case of empty records, as these are not allowed in VHDL
        if 0 == user2regs.num_elements():
            user2regs.add_element("dummy : std_logic")
        if 0 == regs2user.num_elements():
            regs2user.add_element("dummy : std_logic")
        #
        vhdl_package.add_declaration(user2regs)        
        vhdl_package.add_declaration(regs2user)
        self._code = str(vhdl_package)
    #
    # Generate VHDL constants for a field
    def to_vhdl_constants(self, field):
        field_name = field.name.upper()
        field_mask = (2 ** field.bitWidth - 1) << field.bitOffset
        code_block = VhdlCodeBlock()
        code_block.statements.append(VhdlStatement("-- Field '%s' of register '%s'\n" % (field.name, field.parent_reg.name)))
        code_block.statements.append(VhdlDeclaration("constant %s : natural := %d;\n" % (self.bitOffset_identifier(field), field.bitOffset)))
        code_block.statements.append(VhdlDeclaration("constant %s : natural := %d;\n" % (self.bitWidth_identifier(field), field.bitWidth)))
        code_block.statements.append(VhdlDeclaration('constant %s : std_logic_vector(31 downto 0) := x"%.8X";\n' % (self.bitMask_identifier(field), field_mask)))
        return code_block    
    #
    # Generate VHDL record types for a register
    def to_vhdl_records(self, register):
        records = []
        # user-writable fields:
        name = "t_%s_user2regs" % (register.name)
        description = "Register '%s'" % register.name
        elements = []
        for f in register.fields:
            if f.access() == "read-only":
                elements.append('%s : %s' % (f.name, self.vhdl_record_name(f)))
        if len(elements) > 0:
            records.append(VhdlRecord(name, description, elements))
        # bus-writable fields:
        name = "t_%s_regs2user" % (register.name)
        description = "Register '%s'" % register.name
        elements = []
        for f in register.fields:
            if f.access() == "read-write" or f.access() == "write-only":
                elements.append('%s : %s' % (f.name, self.vhdl_record_name(f)))       
        if len(elements) > 0:
            records.append(VhdlRecord(name, description, elements))        
        return records 
    #
    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(self._code)
#
# C header generator
#
class CHeaderGenerator(CodeGenerator):
    def __init__(self, module):
        # Register address offsets
        address_offsets = ""
        for r in module.registers:
            address_offsets += '#define %s 0x%.8X\n' % (self.address_identifier(r), r.addressOffset)
        # Field bit offsets
        fields = ""
        for r in module.registers:
            register_name = r.name.upper()
            fields += "//\n"
            fields += "// Fields in register '%s'\n" % register_name
            fields += "//\n"
            for f in r.fields:
                field_name = f.name.upper()
                field_mask = (2 ** f.bitWidth - 1) << f.bitOffset
                fields += "// Field '%s'\n" % f.name
                fields += "#define %s %d\n" % (self.bitOffset_identifier(f), f.bitOffset)
                fields += "#define %s %d\n" % (self.bitWidth_identifier(f), f.bitWidth)
                fields += "#define %s 0x%.8X\n" % (self.bitMask_identifier(f), field_mask)
                fields += "\n"
            fields += "\n"
        module_name = module.name.upper() + "_REGS"
        d = dict(module_name = module_name,
                 address_offsets = address_offsets,
                 fields = fields,
                 json_module_name = module.name,
                 hdlregs_version = HDLREGS_VERSION,
                 date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self._code = c_header_template.substitute(d)
                
    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(self._code)
#
# HTML code generator
#
class HtmlGenerator():
    def __init__(self, module):       
        # HTML overview list
        
        html_overview = indent(4) + '<table id="overview">\n'
        html_cell_class = 'even'
        for r in module.registers:
            html_overview += indent(5) + '<tr><td class="%s"><a class="overview" href="#%s">%s</d></td></tr>\n' % (html_cell_class, r.name, r.name)
            # cycle cell colors:
            if html_cell_class == 'even': html_cell_class = 'odd'
            elif html_cell_class == 'odd': html_cell_class = 'even'
        html_overview += indent(4) + '</table>\n'        
        # HTML detailed description
        html_registers = ""
        for r in module.registers:
            html_registers += self.to_html(r)
        d = dict(module_name=module.name,
                 date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                 hdlregs_version=HDLREGS_VERSION,
                 registers=html_registers,
                 overview=html_overview)
        self._code = HTML_DOC_TEMPLATE.substitute(d)    
        
    def to_html(self, element):
        # Register -> HTML
        if isinstance(element, Register):
            r = element
            fields_sorted = sorted(r.fields, key=lambda field: field.bitOffset, reverse=True)  # sort fields in order of descending bit offset
            fields_html = ""
            for f in fields_sorted:
                fields_html += self.to_html(f)
            str_addressOffset = "0x%.8X" % r.addressOffset
            d = dict(register_name=r.name,
                     register_description=r.description,
                     register_addr_offset=str_addressOffset,
                     register_fields=fields_html)
            return HTML_REGISTER_TEMPLATE.substitute(d)
        # Field -> HTML
        elif isinstance(element, Field):
            if element.bitWidth == 1:
                field_range = element.bitOffset
            else:
                field_range = "%d:%d" % (element.bitOffset + element.bitWidth - 1, element.bitOffset)
            access = element.access()
            if access == "read-write":
                field_access = "RW"
            elif access == "read-only":
                field_access = "R"
            elif access == "write-only":
                field_access = "W"
            d = dict(field_range=field_range,
                     field_name=element.name,
                     field_access=field_access,
                     field_reset=element.reset(),
                     field_description=element.description)
            return HTML_REGISTER_FIELD_TEMPLATE.substitute(d)            
        
    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(self._code)

# ------------------------------------------------------------------------------
# Register file elements: Module, Register and Field classes
#

# A module definition
class Module():
    SUPPORTED_WIDTHS = (32,)  # supported bus widths
    MANDATORY_ELEMENTS = ("name", "description", "width", "registers")
    #
    # Module constructor    
    def __init__(self, json_module):
        # default values:
        self.name = ""        
        for key in json_module.keys():
            if key == "name":
                self.name = json_module[key]
            elif key == "description":
                self.description = json_module[key]
            elif key == "interface":
                self.interface = json_module[key]
            elif key == "width":
                self.width = int(json_module[key])                
            elif key == "registers":
                self.registers = [Register(json_reg, parent_module=self) for json_reg in json_module[key]]
        # check for missing mandatory elements
        for e in self.MANDATORY_ELEMENTS:
            if not hasattr(self, e):
                if(e == 'name'): self.name = '<unnamed>'
                raise ModuleError(self, "missing '%s' element" % e)            
        # check for unsupported elements
        for key in json_module.keys():
            if key not in self.MANDATORY_ELEMENTS:
                raise ModuleError(self, "unsupported element '%s'" % key)
        # check for unsupported width
        if self.width not in self.SUPPORTED_WIDTHS:
            str_supported_widths = ["'%s'" % str(w) for w in SUPPORTED_WIDTHS]
            str_supported_widths = ", ".join(str_supported_widths)
            raise ModuleError(self, "unsupported width '%d' -- HDLRegs currently supports only the following register widths: %s" % (self.width, str_supported_widths))
        # elaborate & check
        self.elaborate()   
        self.check()                 #
    # Check a module
    def check(self):
        pass
    #
    # Elaborate a module, i.e. compute values for all undefined parameters such
    # as register addresses, bit field offsets etc.
    def elaborate(self):
        # Register address sanity checks:
        addr_dict = {}
        for reg in self.registers:
            addr = reg.addressOffset
            if addr == None:
                continue            
            if addr_dict.has_key(addr):
                addr_dict[addr].append(reg)
            else:
                addr_dict[addr] = [reg]
        for key in addr_dict.keys():
            # check that no two registers have the same address offset:
            if len(addr_dict[key]) > 1:
                conflicting_regs = [r.name for r in addr_dict[key]]    
                conflicting_regs = ", ".join(conflicting_regs)           
                raise(ModuleError(self, "registers [%s] have the same addressOffset" % conflicting_regs))
        #
        # Allocate register addresses
        for r1 in self.registers:
            if r1.addressOffset == None:
                # Register has not been assigned an address offset -> compute the 
                # next available one
                candidate_addressOffset = 0x0
                while(True):
                    success = True
                    for r2 in self.registers:
                        if r2.addressOffset == candidate_addressOffset:
                            candidate_addressOffset += 4
                            success = False
                            break
                    if success:
                        break
                # print "elaboration: allocated address 0x%.8X for register %s" % (candidate_addressOffset, r1.name)
                r1.addressOffset = candidate_addressOffset
            r1.elaborate()

# A register definition 
class Register:
    MANDATORY_ELEMENTS = ("name", "description")
    OPTIONAL_ELEMENTS = ("access", "addressOffset", "reset", "fields")
    ACCESS = ("read-write", "read-only", "write-only")  # supported access-types
    #
    # Register constructor
    def __init__(self, json_reg, parent_module):
        #
        # default values:
        self.parent_module_ = parent_module
        self.name = ""
        self.description = None
        self.access = "read-write"
        self.addressOffset = None
        self._reset = 0                                
        self.fields = []        
        #
        # initialize fields from JSON    
        for key in json_reg.keys():
            if key == "name":
                self.name = json_reg[key]
            elif key == "description":
                self.description = json_reg[key]
            elif key == "access":
                self.access = json_reg[key]
            elif key == "addressOffset":
                self.addressOffset = int_from_json(json_reg[key])
            elif key == "reset":
                self._reset = int_from_json(json_reg[key])                                
            elif key == "fields":
                self.fields = [Field(json_field, self) for json_field in json_reg[key]]
        #
        # check for missing mandatory elements
        for e in self.MANDATORY_ELEMENTS:
            if not hasattr(self, e):
                if(e == 'name'): self.name = '<unnamed>'
                raise RegisterError(self, "missing '%s' element" % e)
        #
        # check for unsupported elements
        for key in json_reg.keys():
            if key not in self.MANDATORY_ELEMENTS + self.OPTIONAL_ELEMENTS:
                raise RegisterError(self, "unsupported element '%s'" % key)
        #
        # elaborate & check
        self.elaborate()   
        self.check()     
    #
    # Returns only the register's bus-writable fields
    def bus_writable_fields(self):
        result = []
        for f in self.fields:
            if f.access() == "write-only" or f.access() == "read-write":
                result += f
        return f
    #
    # Returns True if the register is bus-writable, i.e. if it has at least one bus-writable field
    def is_bus_writable(self):
        for f in self.fields:
            if f.access() == "write-only" or f.access() == "read-write":
                return True        
        return False
    #
    # Returns True if the register is bus-readable, i.e. if it has at least one bus-readable field
    def is_bus_readable(self):
        for f in self.fields:
            if f.access() == "read-only" or f.access() == "read-write":
                return True        
        return False        #
    # Returns True if the register is user-writable, i.e. if it has at least one user-writable field
    def is_user_writable(self):
        for f in self.fields:
            if f.access() == "read-only":
                return True
        return False 
    #
    # Get a registers's reset value        
    def reset(self):
        reset = self._reset  # this is the default reset value, which may be overridden on a field basis
        for f in self.fields:
            if f.has_reset():
                and_mask = ~((2 ** f.bitWidth - 1) << f.bitOffset)
                reset &= and_mask
                or_mask = f.reset() << f.bitOffset
                reset |= or_mask        return reset
    #
    # Get a registers's size
    def size(self):
        return self.parent_module_.width
    #
    # Check the register
    def check(self):
        # check name
        if not is_valid_identifier(self.name):
            raise RegisterError(self, "'%s' is not a valid identifier (it may be a reserved C or VHDL keyword)" % self.name)
        #
        # check access
        if self.access not in self.ACCESS:
            raise RegisterError(self, "'%s' is not a valid access mode" % self.access)
        #
        # check reset value        
        if(self._reset < 0 or self._reset > 2 ** self.size() - 1):
            raise(RegisterError(self, "reset value (%d) is of out range" % self._reset))
        #
        # Check that the register is wide-enough to hold all the bit fields
        bit_field_total_length = 0
        for field in self.fields:
            bit_field_total_length += field.bitWidth
        if bit_field_total_length > self.size():
            raise(RegisterError(self, "not enough bits for all fields"))
    #     
    # Elaborate the register
    def elaborate(self):
        # If the register has no fields, allocate one artificial field spanning the whole register
        if len(self.fields) == 0:
            d = dict(name=self.name, description=self.description, bitWidth=self.size())
            field = Field(d, self) 
            self.fields.append(field)            
        # Try to allocate the missing bit fields
        bits = [None] * self.size()  # list of allocated bits
        for field in self.fields:
            if field.bitOffset != None:
                for i in range(field.bitOffset, field.bitOffset + field.bitWidth):
                    if(i < 0 or i >= self.size()):
                        error("Field '%s' has bits outside of register '%s'" % (field.name, self.name))
                    # print "bit %d of register %s fixed to field %s" % (i, self.name, field.name)
                    bits[i] = field

        # print ["%d: %d" % (i, bits[i] != None) for i in range(len(bits))]

        for field in self.fields:
            if field.bitOffset == None:  # unfixed field
                success = False
                for start_pos in range(self.size()):
                    if bits[start_pos] != None:
                        continue
                    num_bits_available = 1
                    for bitOffset in range(1, self.size() - start_pos):
                        if bits[start_pos + bitOffset] != None:
                            break;
                        num_bits_available += 1
                    # print "start position %d: %d bits available" % (start_pos, num_bits_available)
                    if num_bits_available >= field.bitWidth:
                        field.bitOffset = start_pos
                        print "elaboration: allocated field %s of register %s to bit offset %d" % (field.name, self.name, start_pos)
                        for i in range(start_pos, start_pos + field.bitWidth):
                            bits[i] = field
                        # print ["%d: %d" % (i, bits[i] != None) for i in range(len(bits))]
                        success = True
                        break
                if not success:
                    error("could not allocate field %s in register %s" % (field.name, self.name))
        for field in self.fields:
            field.elaborate()    
    
# A register field        
class Field:
    MANDATORY_ELEMENTS = ("name", "description", "bitWidth")
    OPTIONAL_ELEMENTS = ("bitOffset", "reset", "access")
    #
    # Field constructor    
    def __init__(self, json_field, parent_reg):
        #
        # default values:
        self.parent_reg = parent_reg
        self.name = ""
        self.description = None
        self.bitWidth = None
        self.bitOffset = None
        self._reset = None
        self._access = None
        #
        # initialize fields from JSON    
        for key in json_field.keys():
            if key == "name":
                self.name = json_field[key]
            elif key == "description":
                self.description = json_field[key]
            elif key == "bitWidth":
                self.bitWidth = json_field[key]
            elif key == "bitOffset":
                self.bitOffset = int_from_json(json_field[key])
            elif key == "reset":
                self._reset = int_from_json(json_field[key])
            elif key == "access":
                self._access = json_field[key]
            else:
                raise FieldError(self, "unsupported element '%s'" % key)                 
        #
        # check for missing mandatory elements
        for e in self.MANDATORY_ELEMENTS:
            if not hasattr(self, e):
                if(e == 'name'): self.name = '<unnamed>'
                raise ModuleError(self, "missing '%s' element" % e)
        #
        # check for unsupported elements
        for key in json_field.keys():
            if key not in self.MANDATORY_ELEMENTS + self.OPTIONAL_ELEMENTS:
                raise RegisterError(self, "unsupported element '%s'" % key)                                
        #
        # elaborate & check
        self.elaborate()   
        self.check()     
    #
    # Checks a field (before code generation)     
    def check(self):
        #
        # check name
        if not is_valid_identifier(self.name):
            raise FieldError(self, "'%s' is not a valid identifier (it may be a reserved C or VHDL keyword)" % self.name)                
        if(self.bitWidth == None):
            raise FieldError(self, "missing bit width")
        if(self.bitWidth <= 0 or self.bitWidth > self.parent_reg.size()):
            raise FieldError(self, "bit width is out of range")        
        if(self.bitOffset != None):
            if self.bitOffset < 0 or self.bitOffset >= self.parent_reg.size():
                raise FieldError(self, "bit offset outside of register bounds")
            if self.bitOffset + self.bitWidth - 1 >= self.parent_reg.size():
                raise FieldError(self, "out of register bounds")
        if(self._reset != None):
            if(self._reset < 0):
                raise FieldError(self, "reset value out of range")
            if(self._reset > 2 ** self.bitWidth - 1):
                raise FieldError(self, "reset value out of range")
    #
    # Returns the reset value of a field, which may be inherited from the parent register
    def reset(self):
        if self._reset == None:
            reset = self.parent_reg._reset # don't call reset() as this would create an infinite recursion
            reset >>= self.bitOffset
            and_mask = 2 ** self.bitWidth - 1
            reset &= and_mask
            return reset
        else:
            return self._reset
    #
    # Returns True if the field has a dedicated reset value, 
    # False if the reset inherits its reset value from the 
    # parent register.
    def has_reset(self):
        if self.reset == None:
            return False
        else:
            return True
    #
    # Returns the access mode of a field, which may be inherited from the parent register
    def access(self):
        if self._access == None:
            return self.parent_reg.access
        else:
            return self._access            
    #
    # Elaborate a field, i.e. compute values for all undefined parameters
    def elaborate(self):
        pass
    #
    # Returns True if the field is bus-writable
    def is_bus_writable(self):
        if self.access() == "write-only" or self.access() == "read-write":
            return True   
        return False
    #
    # Returns True if the field is bus-readable
    def is_bus_readable(self):
        if self.access() == "read-only" or self.access() == "read-write":
            return True   
        return False
    #
    # Returns True if the field is user-writable
    def is_user_writable(self):
        if self.access() == "read-only":
            return True   
        return False
# ------------------------------------------------------------------------------
# Exceptions
#
    
class FieldError(Exception): 
    def __init__(self, field, message):
        Exception.__init__(self, "'%s': %s" % (field.name, message))

class RegisterError(Exception): 
    def __init__(self, register, message):
        if len(register.name) == 0:
            register.set_name('<unnamed>')
        Exception.__init__(self, "'%s': %s" % (register.name, message))
    
class ModuleError(Exception): 
    def __init__(self, module, message):
        Exception.__init__(self, "'%s': %s" % (module.name, message))
            
# ------------------------------------------------------------------------------
# Function definitions
#

#
# Convert json element (i.e. integer or string) to integer
#
def int_from_json(json):
    if type(json) == int:
        return json
    else:    
        if json.startswith("0x"):
            return int(json, 16)
        else:
            return int(json, 10)

#
# Checks whether the given string is a valid VHDL basic identifier:
#   basic_identifier ::=
#     letter { [ underline ] letter_or_digit } 
#
def is_valid_identifier(str):
    if len(str) == 0: 
        return False
    if str.lower() in RESERVED_VHDL_KEYWORDS:
        return False
    if str in RESERVED_C_KEYWORDS:
        return False
    pattern = r'[a-zA-Z](_?[a-zA-Z0-9])*$'
    if re.match(pattern, str):
        return True
    else:
        return False
    
def indent(level):
    return " " * INDENTATION_WIDTH * level    
    
# ------------------------------------------------------------------------------
# The main() function
#
if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print "usage: python hdlregs.py <register definition file>"
        sys.exit(-1)
        
    try:
        register_definition_file = sys.argv[1]
        
        # Check for non-ascii characters in JSON file, as these are not supported yet
        num_ascii_errors = 0
        with open(register_definition_file, 'r') as f:
            line_number = 1
            for line in f:
                for char in line:
                    if ord(char) > 127:
                        print "Error in line %d: detected non-ascii character '%c'" % (line_number, char)
                        num_ascii_errors += 1
                line_number += 1
        if num_ascii_errors > 0:
            sys.exit(-1)
        
        # Load JSON file
        json_data = json.load(open(register_definition_file, 'r'))
        module = Module(json_data)
           
        # Write HTML output
        g = HtmlGenerator(module)
        g.save(module.name + '_regs.html')

        # Write C header
        g = CHeaderGenerator(module)
        g.save(module.name + '_regs.h')

        # Write VHDL package
        g = VhdlPackageGenerator(module)
        g.save(module.name + '_regs_pkg.vhd')

        # Write VHDL component
        g = VhdlComponentGenerator(module)
        g.save(module.name + '_regs.vhd')
                            
    except RegisterError as ex:
        print "Error in register " + str(ex)
    
    except FieldError as ex:
        print "Error in field " + str(ex)
    
    except ModuleError as ex:
        print "Error in module " + str(ex)        

