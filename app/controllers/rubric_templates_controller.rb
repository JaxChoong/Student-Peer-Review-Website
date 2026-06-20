class RubricTemplatesController < ApplicationController
  before_action :require_lecturer

  def create
    @template = current_user.rubric_templates.build(template_params)

    if save_template_with_criteria(@template)
      redirect_to customizations_path, notice: "Rubric template created successfully."
    else
      redirect_to customizations_path, alert: "Failed to create rubric template. Please ensure all fields are valid."
    end
  end

  def update
    @template = current_user.rubric_templates.find_by(id: params[:id])
    return redirect_to customizations_path, alert: "Template not found." unless @template

    @template.template_name = params[:rubric_template][:template_name]

    if save_template_with_criteria(@template)
      redirect_to customizations_path, notice: "Rubric template updated successfully."
    else
      redirect_to customizations_path, alert: "Failed to update rubric template."
    end
  end

  def destroy
    @template = current_user.rubric_templates.find_by(id: params[:id])
    if @template
      @template.destroy
      redirect_to customizations_path, notice: "Rubric template deleted."
    else
      redirect_to customizations_path, alert: "Template not found."
    end
  end

  def preview
    @template = RubricTemplate.find_by(id: params[:id])
    if @template
      render partial: 'rubric_templates/preview', locals: { template: @template }
    else
      head :not_found
    end
  end

  private

  def template_params
    params.require(:rubric_template).permit(:template_name)
  end

  def save_template_with_criteria(template)
    ActiveRecord::Base.transaction do
      template.save!
      
      # For update, we clear existing criteria and columns completely
      template.rubric_criteria.destroy_all unless template.new_record?

      if params[:rubric_template][:criteria].present?
        params[:rubric_template][:criteria].each do |_, crit_data|
          next if crit_data[:label].blank?

          criteria = template.rubric_criteria.create!(
            label: crit_data[:label],
            position: crit_data[:position]
          )

          if crit_data[:columns].present?
            crit_data[:columns].each do |_, col_data|
              # Clean descriptions array (split by newline if sent as text, or reject empty if array)
              descriptions = []
              if col_data[:descriptions].is_a?(Array)
                descriptions = col_data[:descriptions].reject(&:blank?)
              elsif col_data[:descriptions].is_a?(String)
                descriptions = col_data[:descriptions].split("\n").map(&:strip).reject(&:blank?)
              end

              criteria.rubric_columns.create!(
                weight: col_data[:weight].to_i,
                position: col_data[:position],
                descriptions: descriptions
              )
            end
          end
        end
      end
      true
    end
  rescue ActiveRecord::RecordInvalid => e
    Rails.logger.error "Rubric template save failed: #{e.message}"
    false
  end
end
