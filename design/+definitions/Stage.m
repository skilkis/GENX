classdef Stage < definitions.Constants
    %Stage Value class inter-stage properties

    % Variables:
    % U = Peripheral Velocity [m/s]
    % c = Absolute Velocity [m/s]
    % w = Relative Velocity [m/s]

    % Subscripts:
    % x = Axial Velocity
    % 1 = Nozzle Inlet
    % 2 = Rotor Inflow
    % 3 = Rotor Outflow

    properties (SetAccess = private)
        w                       % Specific Work Expected of the Stage
        omega                   % Angular Velocity at Mean Radius [rad/s]
        psi                     % Stage Loading Coefficient [-]
        phi                     % Flow Coefficient [-]
        R                       % Degree of Reaction [-]
        inflow                  % Inflow State Variables
        outflow                 % Outflow State Variables
        index                   % Order of the stage within the Turbine
    end
    
    properties (Dependent, SetAccess = private)
        U                       % Perhipheral Velocity [m/s]
        r_m                     % Mean Radius
        c_x                     % Axial velocity
        c_1                     % Absolute Velocity at Nozzle Inflow
        c_2                     % Absolute Velocity at Rotor Inflow
        alpha_1 = atan((R - 1 + 0.5*psi) / phi);
        alpha_2 = atan((1 - R + 0.5*psi) / phi);
        beta_2 = atan((0.5*psi - R) / phi);
        beta_3 = atan((0.5*psi + R) / phi);
        zeta_n                  % Nozzle Solderberg Loss Coefficient
        zeta_r                  % Rotor Solderberg Loss Coefficient
    end
    
    methods
        function obj = Stage(varargin)
            % Creates optional arguments for all state variables
            args = inputParser; % Analyzes passed arguments
            
            addRequired(args, 'eta_tt')
            addRequired(args, 'inflow', @definitions.Validators.validFlow)
            addRequired(args, 'psi')
            addRequired(args, 'phi')
            addRequired(args, 'R')
            addRequired(args, 'w')

            addOptional(args, 'index', 1)

            parse(args, varargin{:});   
            for field = fieldnames(args.Results)'
                obj.(field{:}) = args.Results.(field{:});
            end
        end

        function value = get.U(obj)
            value = sqrt(obj.w / obj.psi);
        end

        function value = get.r_m(obj)
            value = obj. U / obj.omega;
        end

        function value = get.c_1(obj)
            value = obj.c_x / cos(obj.alpha_1);
        end

        function value = get.c_x(obj)
            value = obj.U * obj.phi;
        end
    end

    methods (Static)
        function value = getLossCoefficient(epsilon)
            % Solderberg Loss Coefficient for simplified case Re = 10e5 &
            % Blade H/l = 3. Input epsilon is in SI degree [deg]
            value = 0.04 * (1 + 1.5 * (epsilon/ 100)^2);
        end
    end
    
end

