classdef Validators
    %VALIDATORS defines validation functions for inputs
    methods (Static)
        function valid = validFlow(flow_obj)
            disp(class(flow_obj))
            if isa(flow_obj, 'definitions.FlowCondition')
                valid = true;
            else
                valid = false;
            end
        end
    end
end

