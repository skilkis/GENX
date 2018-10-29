classdef Constants
    %CONSTANTS Parent-class to allow property access w/o repeat definition
    %   Acts similar to a global variable, change values here if dealing
    %   with different gasses.
    
    properties
        cp_air = 1000           % Specific Heat of Air [J/kg K]
        cp_gas = 1150           % Specific Heat of Gas [J/kg K]
        kappa_air = 1.4         % Spec. Heat Ratio of Air [-]
        kappa_gas = 1.33        % Spec. Heat Ratio of Gas [-]
        gas_constant = 287.05   % Gas Constant [J/kg K]
    end
end

