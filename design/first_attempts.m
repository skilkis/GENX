clc
clear all
close all
%% We WANT TO OPTIMIZE POLYTROPIC EFFICIENCY WHILE MINIMIZING AREA/LENGTH

global kappa eta_tt
psi = 0.5;
R = 0.1;
phi = 0.4;

%% Obtaining Velocity Triangles
% Due to the repeating stage assumption alpha_1 = alpha_3

% Subscripts:
% 1 = Nozzle Inlet
% 2 = Rotor Inlet
% 3 = Rotor Outlet

alpha_1 = atan((R - 1 + 0.5*psi) / phi);
alpha_2 = atan((1 - R + 0.5*psi) / phi);
beta_2 = atan((0.5*psi - R) / phi);
beta_3 = atan((0.5*psi + R) / phi);


%% Obtaining Loss Coefficients
% Solderberg Loss Coefficients for simplified case Re = 10e5 & A = 3
% Subscripts:
% n = Nozzle
% r = Rotor

% These have to be expressed in degrees
epsilon_n = rad2deg(alpha_2);
epsilon_r = rad2deg(beta_2 + beta_3);

% TODO Make this into a function
zeta_n = 0.04 * (1 + 1.5 * (epsilon_n / 100)^2);
zeta_r = 0.04 * (1 + 1.5 * (epsilon_r / 100)^2);

%% step 1 - input entry
p_in = 11e5; % inlet pressure
Tin = 1400; % inlet temperature
PI = 9.3; % pressure ratio
mf = 8.2; % mass flow
rot = 35e3; % rotational speed (RPM)
cp = 1150;
kappa = 1.33;
R = 287; % gas constant

%% Calculating Specific Work from Guessed Polytropic Efficiency
eta_p = 0.910; % Guessed polytropic efficiency (chosen)

Tout = Tin*(1/PI)^((kappa-1)/kappa*eta_p); % outlet temperature
pout = p_in/PI; % outlet pressure
Ws = cp*(Tin - Tout); % Specific work

%% step 4 - number of stage(s) selection
N = 5; % number of stages (chosen)
w = Ws/N; % specific work per stage (Check this value)

%% step 5 - velocity triangles 
U = sqrt(w/psi); % peripheral speed
r_m = U/rot; % mean radius

c_x = U * phi;
c_1 = c_x/cos(alpha_1);

%% Deriving Total to Total Efficiency w/ Loss Coeff
% Variables:
% c = Absolute Velocity
% w = Relative Velocity

% Subscripts:
% c = Absolute Velocity
% 1 = Nozzle Inlet
% 2 = Rotor Inflow
% 3 = Rotor Outflow 
c_2 = c_x / cos(alpha_2);
w_3 = c_x / cos(beta_3);

eta_tt = 1/(1 + (zeta_r*(w_3^2) + zeta_n*(c_2^2))/(2*w));

%% Obtaining Actual Polytropic Efficiency
p_start = p_in;
T = linspace(Tin, Tout, N+1);
disp(T)
for i = 1:N
    t_ratio = T(i+1)/T(i);
    disp(t_ratio)
    p_end = pressure(t_ratio, p_start);
    p_start = p_end;
end

eta_p_final =  (kappa / (kappa - 1)) * (log(Tout/Tin) / log(p_end/p_in));




