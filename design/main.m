clc
clear all
close all

%% Imports
FlowCondition = @definitions.FlowCondition;
DesignVector = @definitions.DesignVector; % TODO use this to make
RunCase = @definitions.RunCase;

%% Provided Parameters in Assignment III
data.inflow = FlowCondition('p0', 11e5,...
                            'T0', 1400,...
                            'm_dot', 8.2,...
                            's', 3362,...
                            'h', 1515.42,...
                            'medium', 'gas');
                        
% Turbine Parameters                   
data.RPM = 35e3;         % Revolutions Per Minute [rev/min]
data.PI = 9.3;           % Expansion Ratio [-]
                   
%% Instantiating Design Vector
x0 = DesignVector({'psi', 1.5, 0.5, 3.0;
                  'phi', 1.2, 0.4, 1.3;
                  'R', 0.5, 0.2, 0.6});
              
%% Optimizer Settings
options.Display         = 'iter-detailed';
options.Algorithm       = 'sqp';
options.FunValCheck     = 'off';
options.DiffMinChange   = 1e-3;         % Minimum delta
options.DiffMaxChange   = 1e-2;         % Maximum delta
options.TolCon          = 1e-6;         % Constraint Tolerance
options.TolFun          = 1e-6;         % Objective Function Tolerance
options.TolX            = 1e-6;         % Design Vector Tolerance

options.MaxIter         = 100;          % Maximum Iterations
              
%% Defining Run-case for Number of Stages from 1-10
tic
N=10;
areas = zeros(N, 1);
etas = zeros(N,1);
runs = {};
for i = 1:N
    run = RunCase(i, x0, options, data);
    run.optimize();
    runs{i} = run;
    areas(i) = run.turbine.area;
    etas(i) = run.turbine.eta_p;
end
toc

%% Plotting Most Efficient Turbine
[M,I] = max(etas);
opt_turbine = runs{1,I}.turbine;
fprintf(['Solver Converged! Polytropic Efficiency = %0.4f \n'...
         'N = %d, psi = %0.2f, phi = %0.2f, R = %0.2f'],...
          M, I, opt_turbine.psi, opt_turbine.phi, opt_turbine.R)
opt_turbine.plotVelocityDiagram();
opt_turbine.plotFlowPath();
opt_turbine.plotEnthalpy();


%% Plotting Efficiency Figure
f = figure('Name', 'StagesEta');
grid on; grid minor; hold on;
plot(1:N, etas, 'LineWidth', 1.5, 'Marker', 'o', 'MarkerFaceColor', 'w')
x = xlabel('Number of Stages $\left[-\right]$');
y = ylabel('Polytropic Efficiency, $\eta_p \left[-\right]$');
t = title('Polytropic Efficiency as a Function of Stage Count');

prop_vector = [x, y, t];
property_cell = {'Interpreter', 'FontSize'};
[value_cell{1:length(prop_vector), 1}] = deal('latex');
[value_cell{1:length(prop_vector), 2}] = deal(14);
set(prop_vector, property_cell, value_cell)
f.GraphicsSmoothing = 'on';
utilities.savefig(f)

%% Plotting Cross Sectional Area Figure
f = figure('Name', 'StageAreas');
grid on; grid minor; hold on;
plot(1:N, areas, 'LineWidth', 1.5, 'Marker', 'o', 'MarkerFaceColor', 'w')
x = xlabel('Number of Stages $\left[-\right]$');
y = ylabel('Cross-Sectional Area $\left[\mathrm{m}^2\right]$');
t = title('Turbine Area as a Function of Stage Count');

prop_vector = [x, y, t];
property_cell = {'Interpreter', 'FontSize'};
[value_cell{1:length(prop_vector), 1}] = deal('latex');
[value_cell{1:length(prop_vector), 2}] = deal(14);
set(prop_vector, property_cell, value_cell)
f.GraphicsSmoothing = 'on';
utilities.savefig(f)

%% Clearing Handles
clear FlowCondition Turbine Design Vector RunCase