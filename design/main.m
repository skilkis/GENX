%%
clc
clear all
close all

%% Imports
FlowCondition = @definitions.FlowCondition;
Turbine = @definitions.Turbine;

%% Given Parameters in Assignment

% Provided Inflow
inflow = FlowCondition('p0', 11e5,...
                       'T0', 1400,...
                       'm_dot', 8.2,...
                       's', 3362,...
                       'h', 1515.42,...
                       'medium', 'gas');
% 
turbine = Turbine(inflow, 'RPM', 35000, 'PI', 9.3);

%% Clearing Handles
clear FlowCondition Turbine
% % 
% isa(inflow, 'definitions.FlowCondition')