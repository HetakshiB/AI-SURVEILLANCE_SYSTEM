import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_html_report(self, incidents):
        # Deduplicate incidents that are too close (e.g., within 5 seconds)
        # in case old data exists or cooldown was bypassed
        unique_incidents = []
        last_times = {}
        
        # Sort by timestamp just in case
        sorted_incidents = sorted(incidents, key=lambda x: x['timestamp'])

        for i in sorted_incidents:
            alert = i['alert']
            try:
                # Try to parse timestamp for comparison
                current_time = datetime.fromisoformat(i['timestamp']).timestamp()
            except:
                # Fallback if format is different
                current_time = 0
            
            if alert not in last_times or (current_time - last_times[alert] > 60):
                unique_incidents.append(i)
                last_times[alert] = current_time

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_filename = f"surveillance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path = os.path.join(self.output_dir, report_filename)

        html_content = f"""
        <html>
        <head>
            <title>AI-SURVEILLANCE SYSTEM REPORT</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; color: #333; }}
                h1 {{ color: #2c3e50; text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }}
                .meta {{ text-align: right; font-style: italic; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #2c3e50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .level-high {{ color: #e74c3c; font-weight: bold; }}
                .level-medium {{ color: #f39c12; font-weight: bold; }}
                .footer {{ margin-top: 40px; text-align: center; font-size: 0.8em; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <h1>AI-SURVEILLANCE SYSTEM REPORT</h1>
            <p class="meta">Generated on: {timestamp}</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Alert Type</th>
                        <th>Severity Level</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
        """

        for i in unique_incidents:
            level_class = f"level-{i['level'].lower()}"
            html_content += f"""
                    <tr>
                        <td>{i['timestamp']}</td>
                        <td>{i['alert']}</td>
                        <td class="{level_class}">{i['level']}</td>
                        <td>{str(i.get('details', ''))}</td>
                    </tr>
            """

        html_content += """
                </tbody>
            </table>
            <div class="footer">
                End of Report - AI-SURVEILLANCE SYSTEM
            </div>
        </body>
        </html>
        """

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return report_path, html_content
