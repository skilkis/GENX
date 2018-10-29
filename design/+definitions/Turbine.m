classdef Turbine < definitions.Constants
    %TURBINE Repeating Stage Turbine
    %   Detailed explanation goes here
    
    properties
        inflow                  % Known Inflow State Variables
        psi = 0.5;              % Work Coefficient [-]
        phi = 0.4;              % Flow Coefficient [-]
        R = 0.5;                % Degree of Reaction [-]
        N = 1;                  % Number of Stages [-]
        stages = struct()       % 
        RPM = 35e3              % Revolutions Per Minute [rev/min]
        PI = 9.3                % Expansion Ratio [-]
    end
    
    properties (Dependent)
        omega
        outflow
        eta_p
%         eta_tt
    end
    
    methods
        function obj = Turbine(varargin)
            % Creates optional arguments for all state variables
            args = inputParser; % Analyzes passed arguments
            
            addRequired(args, 'inflow', @definitions.Validators.validFlow)
            
            exclude = fieldnames(definitions.Constants)';
            exclude = [exclude, 'inflow', 'outflow', 'omega', 'eta_p'];
            for prop = fieldnames(obj)'
                if ~any(strcmp(exclude, prop{:}))
                    addOptional(args, prop{:}, NaN)
                end
            end
              
            % Sets result of all optional arguments for current object
            parse(args, varargin{:});   
            for field = fieldnames(args.Results)'
                obj.(field{:}) = args.Results.(field{:});
            end
        end
        
        %% Dependent Property Getters
        function value = get.omega(obj)
            value = obj.RPM * (2*pi) / 60;
        end
        
        function value = get.eta_p(obj)
            disp('I evaluated')
            value = obj.RPM;
        end
        
        function value = get.outflow(obj)
            disp('I evaluated')
            in = obj.inflow;
            value = definitions.FlowCondition('m_dot', in.m_dot,...
                                              'medium', in.medium);
%             value = definitions.FlowCondition();
        end
        
        function obj = build_stages(obj)
            stage = definitions.Stages
            obj.stages.('Stage_1') = 
    end
    
end

