function D = mydct (S)
  SN = double(S);
  D = zeros(8);
  for i = 0:1:7
    for j = 0:1:7
      if i == 0
        Ci = 1/sqrt(8);
      else
        Ci = 0.5;  
      endif
      if j == 0
        Cj = 1/sqrt(8);
      else
        Cj = 0.5;
      endif
      for x = 0:1:7
        for y = 0:1:7
          D(i+1,j+1) = D(i+1,j+1) + SN(x+1,y+1)*cos((2*x+1)*i*pi/(2*8))*cos((2*y+1)*j*pi/(2*8));
        endfor
      endfor
      D(i+1,j+1) = D(i+1,j+1)*Ci*Cj;
    endfor
   endfor
endfunction
        