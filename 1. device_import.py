import yaml
from django.utils.text import slugify
from extras.scripts import Script, StringVar
from core.models import DataFile
from dcim.models import DeviceType, Manufacturer

class ImportDeviceTypes(Script):
    class Meta:
        name = "Import Device Types from Data Source"
        description = "Parses YAML files from a synced Data Source and creates Device Types."

    vendor_filter = StringVar(
        description="Comma-separated list of vendors to import (e.g., apc,cisco). Leave blank for all.",
        required=False
    )

    def run(self, data, commit):
        vendors = data.get('vendor_filter')
        vendor_list = [v.strip().lower() for v in vendors.split(',')] if vendors else []

        # Find all YAML files in synced Data Sources
        data_files = DataFile.objects.filter(path__endswith='.yaml')
        
        if not data_files.exists():
            self.log_failure("No YAML files found. Ensure your Data Source is synced.")
            return

        for data_file in data_files:
            # Expected path format: "device-types/vendor/model.yaml"
            parts = data_file.path.split('/')
            
            # Skip files not in the device-types directory
            if len(parts) < 3 or parts[0] != 'device-types':
                continue

            vendor_name = parts[1]
            
            # Apply vendor filter if provided
            if vendor_list and vendor_name.lower() not in vendor_list:
                continue

            try:
                # Load content from the DataFile record
                # data_file.data contains the raw bytes
                yaml_content = data_file.data.tobytes().decode('utf-8')
                device_data = yaml.safe_load(yaml_content)
                
                if not device_data or 'model' not in device_data:
                    continue

                # 1. Ensure Manufacturer exists
                m_name = device_data.get('manufacturer', vendor_name)
                manufacturer, created = Manufacturer.objects.get_or_create(
                    name=m_name,
                    defaults={'slug': slugify(m_name)}
                )
                if created:
                    self.log_success(f"Created Manufacturer: {manufacturer}")

                # 2. Create Device Type
                model_name = device_data['model']
                dt_obj, created = DeviceType.objects.get_or_create(
                    manufacturer=manufacturer,
                    model=model_name,
                    defaults={
                        'slug': slugify(model_name),
                        'part_number': device_data.get('part_number', ''),
                        'u_height': device_data.get('u_height', 1),
                        'is_full_depth': device_data.get('is_full_depth', True),
                    }
                )

                if created:
                    self.log_success(f"Created Device Type: {model_name}")
                else:
                    self.log_debug(f"Device Type {model_name} already exists.")

            except Exception as e:
                self.log_failure(f"Error processing {data_file.path}: {str(e)}")

        self.log_info("Sync process completed.")