%%
clc
clear all
close all

%% Imports
FlowCondition = @definitions.FlowCondition;
Turbine = @definitions.Turbine;
DesignVector = @definitions.DesignVector; % TODO use this to make

%% Provided Parameters in Assignment III
global psi phi R N RPM PI
inflow = FlowCondition('p0', 11e5,...
                       'T0', 1400,...
                       'm_dot', 8.2,...
                       's', 3362,...
                       'h', 1515.42,...
                       'medium', 'gas');
                   
% Turbine Parameters                   
RPM = 35e3;         % Revolutions Per Minute [rev/min]
PI = 9.3;           % Expansion Ratio [-]

%% Design Vector Initial Point
psi = 1.5;          % Work Coefficient [-]
phi = 1.2;          % Flow Coefficient [-]
R = 0.5;            % Degree of Reaction [-]
N = 2;              % Number of Stages [-]

%% Instantiating Turbine
turbine = Turbine(inflow, psi, phi, R, N, RPM, PI);
turbine.plotEnthalpy();
turbine.plotVelocityDiagram();

f = figure('Name', 'FlowPath');
grid on; grid minor; hold on;
ref = 0;
area = 0;
for i=1:N
    stage = turbine.stages{i,1};
    m_dot = stage.inflow.m_dot;
    r_m = stage.r_m; c_x = stage.c_x;
    rho = [stage.inflow.rho, stage.midflow.rho, stage.outflow.rho];
    H = stage.inflow.m_dot ./ ((2 * pi * r_m * c_x) .* rho);
    L = H / turbine.A;
    spacing = 0.1*((L(1)+L(2))/2);
    
    % Nozzle Row
    x = [ref, ref, ref + L(1), ref + L(1), ref];
    y = [r_m + 0.5*H(1),r_m - 0.5*H(1), r_m - 0.5*H(2),...
        r_m + 0.5*H(2), r_m + 0.5*H(1)];
    [~, A] = convhull(x,y);
    area = area + A;
    
    plot(x,y, 'Color', 'red', 'Marker', 'o')
    
    % Rotor Row
    ref = ref + L(1) + spacing;
    x = [ref, ref, ref + L(2), ref + L(2), ref];
    y = [r_m + 0.5*H(2),r_m - 0.5*H(2), r_m - 0.5*H(3),...
        r_m + 0.5*H(3), r_m + 0.5*H(2)];
    [~, A] = convhull(x,y);
    area = area + A;
    
    plot(x,y, 'Color', 'blue', 'Marker', 'o')
    spacing = 0.1*((L(2)+L(3))/2);
    ref = ref + L(2) + spacing;
    
    disp(H)
    disp(L)
end
pad_x = 0.05*(max(x));
pad_y = 0.05*(max(y) - min(y));

axis([-pad_x, max(x)+pad_x,...
    (r_m-0.25*max(y))-pad_y, (r_m + 0.25*max(y))+pad_y])
x_lim = get(gca,'XLim');  %# Get the range of the x axis
line(x_lim, [r_m, r_m], 'LineStyle', '-.', 'Color', 'black')
legend('Nozzle', 'Rotor')

x = xlabel('Axial Length $\left[\mathrm{m}\right]$');
y = ylabel('Radius $\left[\mathrm{m}\right]$');
t = title('Meridional Flow Path');

prop_vector = [x, y, t];
property_cell = {'Interpreter', 'FontSize'};
[value_cell{1:length(prop_vector), 1}] = deal('latex');
[value_cell{1:length(prop_vector), 2}] = deal(12);
set(prop_vector, property_cell, value_cell)
f.GraphicsSmoothing = 'on';
utilities.savefig(f)



%% Clearing Handles
clear FlowCondition Turbine
% % 
% isa(inflow, 'definitions.FlowCondition')