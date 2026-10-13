# Quick Setup: 3D Printer Integration

## Overview

Get your VeoGen platform connected to a 3D printer in under 30 minutes. This guide walks through setting up the recommended Qidi Tech Plus4 for automated 3D printing workflows.

## Shopping List

### Required Hardware
- **Qidi Tech Plus4** - $769 (Primary printer)
- **Network Cable** - $10 (For stable connection)
- **Additional Filaments** - $200 (PLA, ABS, PETG starter pack)

### Optional Upgrades  
- **Backup Print Bed** - $50
- **Tool Kit** - $25
- **Filament Storage** - $75

**Total Investment: ~$1,119**

## Step 1: Hardware Setup (15 minutes)

### Unbox and Assemble
1. **Unpack printer** following manufacturer instructions
2. **Remove shipping materials** and protective films
3. **Install print bed** and ensure it's level
4. **Load filament** (start with PLA for testing)

### Network Connection
1. **Connect Ethernet cable** (recommended for stability)
2. **Power on printer** and complete initial setup
3. **Connect to WiFi** as backup (optional)
4. **Note IP address** from printer display

## Step 2: Software Setup (10 minutes)

### Install Slicer Software
```bash
# Download PrusaSlicer (recommended)
wget https://github.com/prusa3d/PrusaSlicer/releases/latest/download/PrusaSlicer-linux-x64.AppImage
chmod +x PrusaSlicer-linux-x64.AppImage

# Or download OrcaSlicer (advanced users)
wget https://github.com/SoftFever/OrcaSlicer/releases/latest/download/OrcaSlicer_Linux_V2.0.0.tar.gz
```

### Configure Printer Profile
1. **Open PrusaSlicer**
2. **Add new printer**: "Generic Klipper Printer"
3. **Set build volume**: 256×256×256mm
4. **Configure temperatures**:
   - PLA: 210°C nozzle, 60°C bed
   - ABS: 250°C nozzle, 100°C bed
   - PETG: 240°C nozzle, 80°C bed

## Step 3: VeoGen Integration (5 minutes)

### Install Python Dependencies
```bash
cd /path/to/veogen
pip install requests websocket-client pillow
```

### Configure Printer Connection
```python
# Create config file: config/printers.yaml
printers:
  - name: "qidi_plus4_main"
    ip: "192.168.1.100"  # Your printer's IP
    api_key: "generate_this_from_printer"
    build_volume: [256, 256, 256]
    materials: ["PLA", "ABS", "PETG", "TPU"]
```

### Test Connection
```python
# Run test script
python scripts/test_printer_connection.py

# Expected output:
# ✅ Printer connected: Operational
# ✅ Temperature: Nozzle: 25°C, Bed: 23°C
# ✅ Integration ready!
```

## Step 4: First Print Test

### Simple Test Print
1. **Download test model**: [VeoGen Test Cube](link-to-test-cube.stl)
2. **Slice in PrusaSlicer**:
   - Material: PLA
   - Quality: 0.2mm Standard
   - Infill: 20%
3. **Save G-code** to `/tmp/test_cube.gcode`

### Submit via VeoGen
```python
# Test automated printing
from integrations.qidi_printer import QidiPrinterController

printer = QidiPrinterController("192.168.1.100", "your_api_key")
result = printer.submit_print_job("/tmp/test_cube.gcode", "test_cube")
print(f"Print started: {result}")
```

## Step 5: Blender MCP Integration

### Test Complete Workflow
```python
# Generate and print a simple object
async def test_complete_workflow():
    # 1. Generate 3D model with Blender MCP
    model = await blender_mcp.create_simple_cube(size=20)
    
    # 2. Export for printing
    stl_file = await blender_mcp.export_stl(model.id)
    
    # 3. Auto-print
    result = await automated_3d_printing_workflow({
        "name": "test_cube",
        "model_file": stl_file,
        "material": "PLA",
        "quality": "standard"
    })
    
    print(f"Complete workflow test: {result}")
```

## Common Issues & Solutions

### Connection Problems
```bash
# Check network connectivity
ping 192.168.1.100

# Check if printer API is responding
curl http://192.168.1.100/api/version

# Expected response: {"api":"0.1","server":"1.0.0"}
```

### Print Quality Issues
| Problem | Cause | Solution |
|---------|-------|----------|
| **Poor adhesion** | Bed not level | Re-level bed, clean surface |
| **Stringing** | Temperature too high | Lower nozzle temp by 5-10°C |
| **Layer shifting** | Belt too loose | Check and tighten belts |
| **Under-extrusion** | Clogged nozzle | Clean or replace nozzle |

### API Errors
```python
# Debug API issues
def debug_printer_api():
    try:
        response = requests.get("http://192.168.1.100/api/printer")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
```

## Material Guide

### Recommended Starting Materials

| Material | Cost/kg | Use Case | Temperature |
|----------|---------|----------|-------------|
| **PLA** | $25 | Prototypes, decorative | 210°C/60°C |
| **ABS** | $28 | Functional parts | 250°C/100°C |
| **PETG** | $32 | Clear parts, food-safe | 240°C/80°C |
| **TPU** | $45 | Flexible parts | 230°C/60°C |

### Material Storage
- **Keep dry**: Use sealed containers with desiccant
- **Temperature control**: Store at room temperature
- **Organization**: Label by material type and color

## Maintenance Schedule

### Daily (5 minutes)
- Check filament level
- Verify bed adhesion
- Clear any failed prints

### Weekly (15 minutes)
- Clean print bed with IPA
- Check belt tension
- Lubricate Z-axis if needed

### Monthly (30 minutes)
- Deep clean nozzle
- Check all connections
- Update firmware if available

## Safety Guidelines

### General Safety
- ⚠️ **Hot surfaces**: Nozzle and bed reach high temperatures
- ⚠️ **Moving parts**: Keep hands clear during operation
- ⚠️ **Ventilation**: Ensure adequate airflow, especially with ABS

### Fire Safety
- 🔥 **Never leave unattended**: Monitor long prints
- 🔥 **Thermal runaway protection**: Ensure enabled in firmware
- 🔥 **Emergency stop**: Know how to quickly stop printer

## Next Steps

### Expand Capabilities
1. **Add more materials**: Nylon, PC, Carbon Fiber
2. **Multiple printers**: Scale to print farm
3. **Post-processing**: Sanding, painting, assembly
4. **Quality control**: Add camera monitoring

### Integration Improvements
1. **Dashboard monitoring**: Real-time status in VeoGen UI
2. **Automated slicing**: AI-optimized print settings
3. **Predictive maintenance**: Schedule based on usage
4. **Remote management**: Full control via VeoGen interface

## Support

### Getting Help
- **VeoGen Docs**: `/docs/integrations/3d-printer-integration.md`
- **Printer Manual**: Qidi Tech Plus4 documentation
- **Community**: VeoGen Discord #3d-printing channel

### Troubleshooting Resources
- **Printer diagnostics**: `python scripts/printer_diagnostics.py`
- **Log files**: Check `/var/log/veogen/printer.log`
- **Network tools**: `nmap`, `ping`, `curl` for connectivity testing

---

**🎉 Congratulations!** Your VeoGen platform is now connected to a 3D printer. You can generate digital designs with Blender MCP and automatically print them as physical objects.

**What's Next?** Try generating a phone stand or desk organizer using VeoGen's Blender scripts, then watch it come to life on your 3D printer! 