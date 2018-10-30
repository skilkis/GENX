clear all; close all;

%% step 1 - input entry
pin = 11e5; % inlet pressure
Tin = 1400; % inlet temperature
PI = 9.3; % pressure ratio
mf = 8.2; % mass flow
rot = 35e3; % rotational speed (RPM)
cp = 1150;
kappa = 1.33;
R = 287; % gas constant

%% step 2
pe = 0.92; % polytropic efficiency (chosen)

Tout = Tin*(1/PI)^((kappa-1)/kappa*pe); % outlet temperature
pout = pin/PI; % outlet pressure
Ws = cp*(Tin - Tout); % Specific work

%% step 3 - parameters selection
lambda = 2; % load coef. (chosen)
reac = 0.5; % degree of reaction (chosen)
phi = 1; % flow coef. (chosen)

%% step 4 - number of stage(s) selection
N = 3; % number of stages (chosen)
w = Ws/N; % specific work per stage (Check this value)

% Verification turbopi
%w = 1;

%% step 5 - velocity triangles 
U = sqrt(w/lambda); % peripheral speed  WHY IS IT FACTOR 2?
rot = rot*2*pi/60; % rotational speed (rad/s)
Rm = U/rot; % mean radius, why is mean radius computed from U?

%This is defined for the rotor
vm = phi*U; % meridional speed
A1 = atan((lambda/4+1-reac)/phi); % alpha 1
B2 = atan(tan(A1)-1/phi-lambda/(2*phi)); 
B1 = atan(tan(A1)-1/phi); 
A2 = atan(tan(B2)+1/phi); 
v1 = vm/cos(A1);
w1 = vm/cos(B1);
v2 = vm/cos(A2);
w2 = vm/cos(B2);

% Verification with turbopi if necessary
%A1 = radtodeg(A1)
%B2 = radtodeg(B2)
%B1 = radtodeg(B1) 
%A2 = radtodeg(A2)

%% step 5 (bis) - inter-stage thermodynamic properties
T = linspace(Tin,Tout,2*N+1); % temperature at each stage, assumed to vary linearly due to equal work of each stage
p = []; p(1) = pin;
for k = 1:2*N
    p(k+1) = p(k)*(T(k+1)/T(k))^(kappa/pe/(kappa-1)); % pressure at each stage
end

% Factor of 2 is only for R=0.5
%% step 6 - blade heights determination 
ro = p./(R*T); % density at each stage % This has to be converted into static temperature
hb = mf./(2*pi*Rm*ro*vm); % blade heights

%% step 7 - blade length (axial chord)
b = 1.5*mean(hb)*ones(1,2*N); % blade length

%% step 8 - plots

%------------------------------ flow-path ---------------------------------

rmax = Rm + hb/2; Rmax = []; % blade maximal radius
rmin = Rm - hb/2; Rmin = []; % blade minimal radius
length = [0 cumsum(b)]; Length = [];
d = 0.2*b(1); % space in between stages

for k = 1:2*N
    Length = [Length length(k)+(k-1)*d length(k+1)+(k-1)*d];
    Rmax = [Rmax rmax(k) rmax(k+1)];
    Rmin = [Rmin rmin(k) rmin(k+1)];
end

figure(1)
plot([Length(1)-d Length(end)+d], [Rm Rm], 'Black--'); hold on; grid on;

for k = 2*(1:N)
    plot(Length([2*k-1 2*k]), Rmax([2*k-1 2*k]), 'r');
    plot(Length([2*k-1 2*k]), Rmin([2*k-1 2*k]), 'r');
    plot([Length(2*k-1) Length(2*k-1)], [Rmin(2*k-1) Rmax(2*k-1)], 'r');
    plot([Length(2*k) Length(2*k)], [Rmin(2*k) Rmax(2*k)], 'r');
    plot(Length(2*k-1), Rmax(2*k-1), 'ro'); plot(Length(2*k), Rmax(2*k), 'ro');
    plot(Length(2*k-1),Rmin(2*k-1), 'ro'); plot(Length(2*k),Rmin(2*k), 'ro'); 
    
    k = k-1;
    plot(Length([2*k-1 2*k]), Rmax([2*k-1 2*k]), 'b');
    plot(Length([2*k-1 2*k]), Rmin([2*k-1 2*k]), 'b');
    plot([Length(2*k-1) Length(2*k-1)], [Rmin(2*k-1) Rmax(2*k-1)], 'b');
    plot([Length(2*k) Length(2*k)], [Rmin(2*k) Rmax(2*k)], 'b');
    plot(Length(2*k-1), Rmax(2*k-1), 'bo'); plot(Length(2*k), Rmax(2*k), 'bo');
    plot(Length(2*k-1),Rmin(2*k-1), 'bo'); plot(Length(2*k),Rmin(2*k), 'bo'); 
end
title('Meridional flow path'); xlabel('Axial length [m]'); ylabel('Radius [m]');
axis([Length(1)-d Length(end)+d Rmin(end)-d Rmax(end)+d]);

%------------------------------ h-s diagram -------------------------------

s = [3362]; % entropy [J*K/kg]
h = [1515.42]; % enthalpy [kJ/kg]
for k = 1:2*N
    s(k+1) = s(k) + cp*log(T(k+1)/T(k)) - R*log(p(k+1)/p(k)); % entropy at each point
    h(k+1) = h(k) + cp/1000*(T(k+1)-T(k)); % enthalpy at each point
end

figure(2)
plot(s,h,'r+'); hold on; grid on;
plot(s,h,'r');

Tvar = 700:1500;
for k = 1:2*N+1
    hvar = h(k) + cp/1000*(Tvar - T(k));
    svar = s(k) + cp*log(Tvar/T(k));
    plot(svar, hvar, 'black--');
end

title('h-s diagram'); xlabel('s [J*K/kg]'); ylabel('h [kJ/kg]');
axis([3360 3420 800 1600]);