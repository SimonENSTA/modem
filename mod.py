import numpy as np
import 


# Instance variables
fe = 8000
f1=2000
f2=500
dt =1/fe
t=[0:dt:(0.004-dt)]
t=linspace( 0, 2*pi, 100 ) 


b1=randn(1,length(t));
b2=randn(1,length(t));
S1=sin(2*pi*f1*t+10)+b1/2;
S2=sin(2*pi*f2*t+10)+b2/2;

hold on
plot(t,S1)
plot(t,S2,'r')
hold off


T=[];
A=[0 1 0 1 1 0 1 0 0];

for i=1:length(A)
    if A(i)==1
        T=[T S1];
    else
        T=[T S2];
    end
end

% plot(T);grid on

% % wavplay(T,Fe);
[b,a] = butter(4,0.9,'low');
y=filter(b,a,T);
[b,a] = butter(2,0.1,'low');
y=filter(b,a,y);
plot(abs(y));
grid;
