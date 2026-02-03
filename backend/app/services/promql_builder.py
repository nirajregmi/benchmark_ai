from typing import Optional, List

def build_promql_query(metric_type: str, resource_name: Optional[str] = None, selected_pods: Optional[List[str]] = None) -> str:
    """
    Constructs a PromQL query based on metric type and resource filter.
    Prioritizes selected_pods if provided.
    """
    # Sanitize inputs (basic)
    resource_filter = ""
    if selected_pods and len(selected_pods) > 0:
        # Create regex for multiple pods: (pod1|pod2)
        pods_regex = "|".join(selected_pods)
        resource_filter = f'{{pod=~"{pods_regex}"}}'
    elif resource_name:
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
            
    elif metric_type == "cpu_throttling":
        if resource_filter:
            return f'sum by (pod) (rate(container_cpu_cfs_throttled_seconds_total{resource_filter}[5m]))'
        else:
            return 'sum(rate(container_cpu_cfs_throttled_seconds_total[5m]))'

    else:
        # Default fallback or "unknown" intent
        return 'up' 