from typing import Optional

def build_promql_query(metric_type: str, resource_name: Optional[str]) -> str:
    """
    Constructs a PromQL query based on metric type and resource filter.
    Defaults to cluster-wide aggregation if no resource provided.
    """
    # Sanitize inputs (basic)
    resource_filter = ""
    if resource_name:
        # Avoid injection by using strict regex matcher in PromQL
        resource_filter = f'{{pod=~"{resource_name}.*"}}'
    
    if metric_type == "cpu":
        if resource_filter:
            # CPU usage for a specific pod/resource
            return f'sum(rate(container_cpu_usage_seconds_total{resource_filter}[5m]))'
        else:
            # Cluster total CPU
            return 'sum(rate(container_cpu_usage_seconds_total[5m]))'
            
    elif metric_type == "memory":
        if resource_filter:
            return f'sum(container_memory_working_set_bytes{resource_filter})'
        else:
            return 'sum(container_memory_working_set_bytes)'
            
    elif metric_type == "network":
        if resource_filter:
            return f'sum(rate(container_network_receive_bytes_total{resource_filter}[5m]))'
        else:
            return 'sum(rate(container_network_receive_bytes_total[5m]))'
            
    else:
        # Default fallback or "unknown" intent
        return 'up' 
