import io
from datetime import datetime

from matplotlib import pyplot as plt

from report_gen.models.timestamp_series import TimestampSeries


def line_chart_bytes(series: TimestampSeries, x_label: str, y_label: str, title: str, dpi: int = 300,
                     color: str = 'blue') -> bytes:
    """
    Generates a line chart and returns it as a byte array.
    :param series: TimestampSeries object containing x (timestamps) and y (values)
    :param x_label: Label of the x-axis
    :param y_label: Label of the y-axis
    :param title: Title of the chart
    :param dpi: Dots per inch for the image quality
    :param color: Color of the line in the chart
    :return: Byte array of the generated chart image
    :raises ValueError: If series is None, empty, or has mismatched lengths
    """
    # Validate input
    if series is None:
        raise ValueError("Series cannot be None")
    
    if not series.timestamps or not series.values:
        raise ValueError("Series timestamps and values cannot be empty")
    
    if len(series.timestamps) != len(series.values):
        raise ValueError(f"Timestamps length ({len(series.timestamps)}) must match values length ({len(series.values)})")
    
    buffer = io.BytesIO()
    
    try:
        # Ensure all timestamps are datetime objects for plotting
        x = []
        for dt in series.timestamps:
            if isinstance(dt, datetime):
                x.append(dt)
            elif isinstance(dt, (int, float)):
                x.append(datetime.fromtimestamp(float(dt)))
            elif isinstance(dt, str):
                # Try parsing string as ISO format or timestamp
                try:
                    x.append(datetime.fromisoformat(dt))
                except ValueError:
                    x.append(datetime.fromtimestamp(float(dt)))
            else:
                raise ValueError(f"Unsupported timestamp type: {type(dt)}")
        
        y = series.values
        
        # Create minimal clean plot
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
        
        # Simple clean line without markers
        ax.plot(x, y, linewidth=2, color=color, alpha=0.85, linestyle='-', antialiased=True)
        
        # Minimal title and labels
        ax.set_title(title, fontsize=14, fontweight='600', pad=15, 
                    color='#2c3e50', family='sans-serif')
        ax.set_xlabel(x_label, fontsize=11, color='#34495e', labelpad=8)
        ax.set_ylabel(y_label, fontsize=11, color='#34495e', labelpad=8)
        
        # Subtle grid
        ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#bdc3c7')
        ax.set_axisbelow(True)
        
        # Clean minimal spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#d5d8dc')
        ax.spines['bottom'].set_color('#d5d8dc')
        ax.spines['left'].set_linewidth(1)
        ax.spines['bottom'].set_linewidth(1)
        
        # Minimal tick styling
        ax.tick_params(colors='#7f8c8d', labelsize=9, length=4, width=1)
        
        # Format x-axis dates
        fig.autofmt_xdate(rotation=45)
        plt.tight_layout()
        
        # Save to buffer
        fig.savefig(buffer, format='png', dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        
        # Return bytes
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        # Clean up matplotlib resources
        plt.close('all')
        raise RuntimeError(f"Failed to generate line chart: {str(e)}") from e
    finally:
        # Ensure buffer is closed if an error occurs
        if buffer and not buffer.closed:
            pass  # Keep buffer open to return data
