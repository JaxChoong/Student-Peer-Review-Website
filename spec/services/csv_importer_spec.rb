require 'rails_helper'
require 'csv'

RSpec.describe CsvImporter do
  let!(:lecturer) { create(:user, role: 'lecturer') }
  let(:temp_dir) { Dir.mktmpdir }

  after do
    FileUtils.remove_entry temp_dir
  end

  def create_csv(filename, headers, rows)
    filepath = File.join(temp_dir, filename)
    CSV.open(filepath, "w") do |csv|
      csv << headers
      rows.each { |r| csv << r }
    end
    filepath
  end

  describe '.call' do
    context 'with a valid CSV file' do
      let(:filepath) do
        create_csv('valid.csv', 
          ['email', 'name', 'studentId', 'section', 'group'], 
          [
            ['john@mmu.edu.my', 'John Doe', '1191100000', 'TC2L', 'Group 1'],
            ['jane@mmu.edu.my', 'Jane Smith', '1191100001', 'TC2L', 'Group 1'],
            ['alice@mmu.edu.my', 'Alice Wong', '1191100002', 'TC3L', 'Group 2']
          ]
        )
      end

      it 'returns success true' do
        result = CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        expect(result[:success]).to be true
      end

      it 'creates a new course' do
        expect {
          CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        }.to change(Course, :count).by(1)
        
        course = Course.last
        expect(course.lecturer_id).to eq(lecturer.id)
      end

      it 'creates users with correct roles and attributes' do
        expect {
          CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        }.to change(User, :count).by(3)

        john = User.find_by(email: 'john@mmu.edu.my')
        expect(john.name).to eq('John Doe')
        expect(john.student_number).to eq('1191100000')
        expect(john.role).to eq('student')
      end

      it 'creates sections and groups correctly' do
        CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        course = Course.last

        expect(course.sections.count).to eq(2)
        expect(course.groups.count).to eq(2)

        tc2l = course.sections.find_by(section_code: 'TC2L')
        tc3l = course.sections.find_by(section_code: 'TC3L')
        
        expect(tc2l.groups.first.group_name).to eq('Group 1')
        expect(tc3l.groups.first.group_name).to eq('Group 2')
      end

      it 'creates enrollments and group memberships' do
        CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        john = User.find_by(email: 'john@mmu.edu.my')
        
        expect(john.enrollments.count).to eq(1)
        expect(john.group_memberships.count).to eq(1)
        expect(john.groups.first.group_name).to eq('Group 1')
      end

      it 'returns a list of newly generated passwords' do
        result = CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        expect(result[:new_users].length).to eq(3)
        expect(result[:new_users].first).to contain_exactly('john@mmu.edu.my', 'John Doe', anything)
      end

      context 'when some users already exist' do
        before do
          create(:user, email: 'john@mmu.edu.my', name: 'John Old')
        end

        it 'does not create duplicate users' do
          expect {
            CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
          }.to change(User, :count).by(2) # Only 2 new users, 1 already exists
        end

        it 'enrolls the existing user without resetting their password' do
          result = CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
          
          john = User.find_by(email: 'john@mmu.edu.my')
          expect(john.enrollments.count).to eq(1)
          
          # Only the 2 truly new users should be in the new_users array
          expect(result[:new_users].length).to eq(2)
        end
      end
    end

    context 'with missing required headers' do
      let(:filepath) do
        create_csv('missing.csv', 
          ['name', 'studentId', 'section', 'group'], # missing email
          [['John Doe', '1191100000', 'TC2L', 'Group 1']]
        )
      end

      it 'returns success false and specifies missing headers' do
        result = CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        expect(result[:success]).to be false
        expect(result[:error]).to match(/Missing headers: email/)
      end

      it 'does not create any records' do
        expect {
          CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        }.not_to change(Course, :count)

        expect {
          CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        }.not_to change(User, :count)
      end
    end

    context 'with malformed CSV data' do
      let(:filepath) do
        path = File.join(temp_dir, 'malformed.csv')
        File.write(path, "email,name,section,group\n\"john@mmu.edu.my,John,TC2L,Group 1") # Unclosed quote
        path
      end

      it 'returns success false with error message' do
        result = CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        expect(result[:success]).to be false
        expect(result[:error]).to include("Invalid CSV format")
      end
    end

    context 'with blank rows' do
      let(:filepath) do
        create_csv('blank.csv', 
          ['email', 'name', 'section', 'group'], 
          [
            ['john@mmu.edu.my', 'John Doe', 'TC2L', 'Group 1'],
            [nil, nil, nil, nil]
          ]
        )
      end

      it 'fails validation or raises error properly' do
        result = CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        # Assuming model validation fails on blank email, rolling back transaction
        expect(result[:success]).to be false
        expect(result[:error]).to be_present
      end
      
      it 'rolls back the entire transaction' do
        expect {
          CsvImporter.call(
          lecturer_id: lecturer.id, 
          filepath: filepath,
          course_code: 'CS101',
          course_name: 'Intro to CS',
          start_date: Date.today,
          end_date: Date.today + 1.week
        )
        }.not_to change(User, :count)
      end
    end
  end
end
