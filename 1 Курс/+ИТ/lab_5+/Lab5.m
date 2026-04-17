a=-0.5
b=2.0
for t=0:0.15:3
   if t>2 
       Y=eps.^(a*t)*cos(b*t)
   if t<1
       Y=1
   else
       Y=a*t.^2*log(t)
   end
end

end
