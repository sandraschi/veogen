#!/usr/bin/env python3
"""
Memory Export Script for MCP Knowledge Graph

This script provides functions to export MCP memory knowledge graph data
to various file formats (JSON, Markdown, CSV).

Usage:
    python memory-export-script.py --format json
    python memory-export-script.py --format markdown
    python memory-export-script.py --format csv
"""

import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def export_to_json(entities: List[Dict], relations: List[Dict], output_path: str = None):
    """Export knowledge graph to JSON format."""
    if not output_path:
        output_path = f"memory-export-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    export_data = {
        "export_metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_entities": len(entities),
            "total_relations": len(relations),
            "format": "json"
        },
        "entities": entities,
        "relations": relations
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON export saved to: {output_path}")
    return output_path


def export_to_markdown(entities: List[Dict], relations: List[Dict], output_path: str = None):
    """Export knowledge graph to Markdown format."""
    if not output_path:
        output_path = f"memory-export-{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Memory Export - Knowledge Graph\n\n")
        f.write(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Entities:** {len(entities)}\n")
        f.write(f"**Total Relations:** {len(relations)}\n\n")
        
        f.write("## Entities\n\n")
        for entity in entities:
            f.write(f"### {entity['name']}\n")
            f.write(f"**Type:** {entity['entityType']}\n\n")
            
            if entity.get('observations'):
                f.write("**Observations:**\n")
                for observation in entity['observations']:
                    f.write(f"- {observation}\n")
                f.write("\n")
        
        f.write("## Relations\n\n")
        if relations:
            f.write("| From | Relation | To |\n")
            f.write("|------|----------|----|\n")
            for relation in relations:
                f.write(f"| {relation['from']} | {relation['relationType']} | {relation['to']} |\n")
        else:
            f.write("*No relations defined*\n")
        
        f.write("\n## Memory Categories Overview\n\n")
        memory_categories = [e for e in entities if e['entityType'] == 'MemoryCategory']
        for category in memory_categories:
            f.write(f"- **{category['name']}**: {len(category.get('observations', []))} rules\n")
    
    print(f"✅ Markdown export saved to: {output_path}")
    return output_path


def export_to_csv(entities: List[Dict], relations: List[Dict], output_dir: str = None):
    """Export knowledge graph to CSV format (separate files for entities and relations)."""
    if not output_dir:
        output_dir = f"memory-export-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    Path(output_dir).mkdir(exist_ok=True)
    
    # Export entities
    entities_file = Path(output_dir) / "entities.csv"
    with open(entities_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Type', 'Observations'])
        
        for entity in entities:
            observations = '; '.join(entity.get('observations', []))
            writer.writerow([entity['name'], entity['entityType'], observations])
    
    # Export relations
    relations_file = Path(output_dir) / "relations.csv"
    with open(relations_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['From', 'Relation_Type', 'To'])
        
        for relation in relations:
            writer.writerow([relation['from'], relation['relationType'], relation['to']])
    
    # Export metadata
    metadata_file = Path(output_dir) / "metadata.csv"
    with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Property', 'Value'])
        writer.writerow(['Export_Date', datetime.now().isoformat()])
        writer.writerow(['Total_Entities', len(entities)])
        writer.writerow(['Total_Relations', len(relations)])
        writer.writerow(['Format', 'CSV'])
    
    print(f"✅ CSV export saved to directory: {output_dir}")
    print(f"   - entities.csv: {len(entities)} entities")
    print(f"   - relations.csv: {len(relations)} relations")
    print(f"   - metadata.csv: Export information")
    return output_dir


def create_memory_backup_script(output_path: str = "backup-mcp-memories.py"):
    """Create a script that can restore these memories to MCP."""
    
    backup_script = '''#!/usr/bin/env python3
"""
MCP Memory Backup and Restore Script

This script can restore memory entities and relations to the MCP knowledge graph.
Generated automatically from memory export.
"""

# This would need to be integrated with your MCP client
# The data structure matches what was exported

ENTITIES_TO_RESTORE = [
    # Add exported entities here
]

RELATIONS_TO_RESTORE = [
    # Add exported relations here  
]

def restore_memories():
    """Restore memories to MCP knowledge graph."""
    print("This script template needs to be integrated with your MCP client")
    print("Use the entities and relations data to recreate the knowledge graph")
    
if __name__ == "__main__":
    restore_memories()
'''
    
    with open(output_path, 'w') as f:
        f.write(backup_script)
    
    print(f"✅ Backup script template created: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Export MCP Memory Knowledge Graph')
    parser.add_argument('--format', choices=['json', 'markdown', 'csv', 'all'], 
                       default='all', help='Export format')
    parser.add_argument('--output', help='Output path/directory')
    
    args = parser.parse_args()
    
    # Sample data structure - replace with actual MCP graph data
    sample_entities = [
        {
            "name": "PowerShell Syntax Rules",
            "entityType": "MemoryCategory",
            "observations": [
                "Memory ID 2589190: Never use Linux syntax in scripts or chats",
                "No && for chaining commands or similar Linux operators allowed",
                "Always use proper PowerShell syntax for Windows environment"
            ]
        }
        # Add more entities...
    ]
    
    sample_relations = [
        {
            "from": "VeoGen Project Memories",
            "to": "PowerShell Syntax Rules", 
            "relationType": "contains"
        }
        # Add more relations...
    ]
    
    print("🔄 Exporting MCP Memory Knowledge Graph...")
    
    if args.format in ['json', 'all']:
        export_to_json(sample_entities, sample_relations, args.output)
    
    if args.format in ['markdown', 'all']:
        export_to_markdown(sample_entities, sample_relations, args.output)
    
    if args.format in ['csv', 'all']:
        export_to_csv(sample_entities, sample_relations, args.output)
    
    if args.format == 'all':
        create_memory_backup_script()
    
    print("\n✅ Memory export completed!")


if __name__ == "__main__":
    main() 