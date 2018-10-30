function savefig(fig_h)
%SAVEFIG Formats figure and saves as pdf

    AR=[8 5]; %Aspect Ratio
    Margin=0.15; %Control Figure Margins
    NF=0.01; %Distance to Nudge Plot to Compensate for Axis Labels
    
    if isa(fig_h, 'matlab.ui.Figure')
        name = fig_h.Name;

        % Formatting Aspect Ratio
        set(fig_h, 'InvertHardCopy', 'off');
        set(fig_h, 'PaperPosition', [0 0 AR(1) AR(2)]); 
        set(fig_h, 'PaperSize', [AR(1) AR(2)]);

        % Formatting Axis Position
        axis = get(fig_h,'CurrentAxes');
        set(axis,... %Formatting Alignment
            'Position',[((Margin+NF)/2) ((0+((AR(1)/AR(2))*(Margin)))/2)...
            (1-Margin) (1-((AR(1)/AR(2))*Margin))]);
        
        % Saving Figure
        saveas(fig_h, [pwd '\Figures\' name] , 'pdf')
        
    else
        % FIXME implement method to save multiple figures
        error('Not yet implemented')
    %     for fig = figure_handle
    %     end
    end
end

