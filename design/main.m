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
psi = 1.75;          % Work Coefficient [-]
phi = 1.2;          % Flow Coefficient [-]
R = 0.5;            % Degree of Reaction [-]
N = 1;             % Number of Stages [-]

%% Instantiating Turbine
turbine = Turbine(inflow, psi, phi, R, N, RPM, PI);
% turbine.stages{1,1}.plotVelocityDiagram();

%% Clearing Handles
clear FlowCondition Turbine
% % 
% isa(inflow, 'definitions.FlowCondition')