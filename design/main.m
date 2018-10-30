%%
clc
clear all
close all

%% Imports
FlowCondition = @definitions.FlowCondition;
Turbine = @definitions.Turbine;
DesignVector = @definitions.DesignVector; % TODO use this to make

%% Provided Parameters in Assignment III
% global psi phi R N RPM PI
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
x = DesignVector({'psi', 1.5, 0.5, 3.0;
                  'phi', 1.2, 0.4, 1.3;
                  'R', 0.5, 0.2, 0.6});

%% Instantiating Turbine
turbine = Turbine(inflow, psi, phi, R, N, RPM, PI);
turbine.plotEnthalpy();
turbine.plotVelocityDiagram();
turbine.plotFlowPath();

%% Clearing Handles
clear FlowCondition Turbine
% % 
% isa(inflow, 'definitions.FlowCondition')