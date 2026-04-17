## Copyright (C) 2022 User
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <https://www.gnu.org/licenses/>.

## -*- texinfo -*-
## @deftypefn {} {@var{retval} =} fun2 (@var{input1}, @var{input2})
##
## @seealso{}
## @end deftypefn

## Author: User <User@FOG>
## Created: 2022-04-27

function f = fun2(x)
  f = (2.*x(1).^2-x(2)-3).^2+x(1).^2+2.*x(1)+2;
endfunction
