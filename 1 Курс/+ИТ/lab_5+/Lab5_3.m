A =[];
srsum=0;
k=1;
for i=1:1:100
    A(i) = rand(1,100);
    srsum=srsum + A(i);
    k=k+1;
end
srsum=srsum/k;
disp (srsum)
disp(A)