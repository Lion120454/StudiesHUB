function S = myidct (D)
  S = zeros(8,8);
  for x = 0:1:7
    for y = 0:1:7
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
          S(x+1,y+1) = S(x+1,y+1) + Ci*Cj*D(i+1,j+1)*cos((2*x+1)*i*pi/(2*8))*cos((2*y+1)*j*pi/(2*8));
        endfor
      endfor
    endfor
   endfor
endfunction