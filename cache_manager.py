"""
Cache Manager for Eurostat Data
Stores API responses locally to avoid repeated slow API calls
"""

import os
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Optional
import hashlib


class CacheManager:
    """Manages local file cache for Eurostat data"""
    
    def __init__(self, cache_dir: str = ".eurostat_cache"):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, dataset_id: str, filters: dict) -> str:
        """
        Generate unique cache key for dataset + filters
        
        Args:
            dataset_id: Eurostat dataset ID
            filters: Filter dictionary
            
        Returns:
            Unique string key
        """
        # Sort filters for consistent hashing
        filter_str = json.dumps(filters, sort_keys=True)
        combined = f"{dataset_id}_{filter_str}"
        
        # Use hash for shorter filenames
        hash_obj = hashlib.md5(combined.encode())
        return f"{dataset_id}_{hash_obj.hexdigest()[:8]}"
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get full path to cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.csv")
    
    def _get_metadata_path(self, cache_key: str) -> str:
        """Get full path to metadata file"""
        return os.path.join(self.cache_dir, f"{cache_key}_meta.json")
    
    def get_cached_data(
        self, 
        dataset_id: str, 
        filters: dict,
        max_age_hours: int = 24,
        data_freshness_days: int = 30
    ) -> Optional[pd.Series]:
        """
        Get cached data if available and fresh
        
        Args:
            dataset_id: Eurostat dataset ID
            filters: Filter dictionary
            max_age_hours: Maximum cache file age in hours (default 24)
            data_freshness_days: Maximum age of actual data in days (default 30)
            
        Returns:
            pandas Series with datetime index, or None if cache miss/stale
        """
        try:
            cache_key = self._get_cache_key(dataset_id, filters)
            cache_path = self._get_cache_path(cache_key)
            meta_path = self._get_metadata_path(cache_key)
            
            # Check if cache files exist
            if not os.path.exists(cache_path) or not os.path.exists(meta_path):
                return None
            
            # Check cache file age
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            cached_time = datetime.fromisoformat(metadata['cached_at'])
            cache_age = datetime.now() - cached_time
            
            if cache_age > timedelta(hours=max_age_hours):
                # Cache file is too old
                return None
            
            # Load cached data
            df = pd.read_csv(cache_path, parse_dates=['date'])
            df = df.set_index('date')
            series = df['value']
            
            # Check if the DATA ITSELF is fresh (most recent data point < 30 days old)
            if not series.empty:
                latest_data_date = series.index.max()
                data_age_days = (datetime.now() - latest_data_date).days
                
                if data_age_days > data_freshness_days:
                    # Data is stale, force refresh
                    print(f"  [CACHE STALE DATA] {dataset_id}: latest data {latest_data_date.strftime('%Y-%m-%d')} is {data_age_days} days old")
                    return None
            
            return series
            
        except Exception as e:
            # If any error reading cache, return None (will fetch fresh)
            print(f"Cache read error: {e}")
            return None
    
    def save_to_cache(
        self,
        dataset_id: str,
        filters: dict,
        series: pd.Series
    ) -> bool:
        """
        Save data to cache
        
        Args:
            dataset_id: Eurostat dataset ID
            filters: Filter dictionary
            series: pandas Series with datetime index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(dataset_id, filters)
            cache_path = self._get_cache_path(cache_key)
            meta_path = self._get_metadata_path(cache_key)
            
            # Save data as CSV
            df = pd.DataFrame({'date': series.index, 'value': series.values})
            df.to_csv(cache_path, index=False)
            
            # Save metadata
            metadata = {
                'dataset_id': dataset_id,
                'filters': filters,
                'cached_at': datetime.now().isoformat(),
                'observations': len(series),
                'latest_date': series.index.max().isoformat()
            }
            
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Cache write error: {e}")
            return False
    
    def clear_cache(self, older_than_hours: Optional[int] = None):
        """
        Clear cache files
        
        Args:
            older_than_hours: If provided, only clear files older than this
        """
        try:
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                
                if older_than_hours:
                    # Check file age
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    age = datetime.now() - file_time
                    
                    if age > timedelta(hours=older_than_hours):
                        os.remove(filepath)
                else:
                    # Remove all
                    os.remove(filepath)
            
            print(f"Cache cleared from {self.cache_dir}")
            
        except Exception as e:
            print(f"Cache clear error: {e}")
    
    def get_cache_info(self) -> dict:
        """
        Get information about cache contents
        
        Returns:
            Dict with cache statistics
        """
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.csv')]
            
            total_size = sum(
                os.path.getsize(os.path.join(self.cache_dir, f)) 
                for f in os.listdir(self.cache_dir)
            )
            
            return {
                'cache_dir': self.cache_dir,
                'num_datasets': len(cache_files),
                'total_size_mb': total_size / (1024 * 1024),
                'exists': os.path.exists(self.cache_dir)
            }
            
        except Exception as e:
            return {'error': str(e)}


def test_cache_manager():
    """Test cache functionality"""
    print("\nTesting Cache Manager...")
    
    cache = CacheManager()
    
    # Create test data
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='Q')
    values = [100 + i for i in range(len(dates))]
    test_series = pd.Series(values, index=dates)
    
    # Test save
    print("\n1. Saving test data to cache...")
    success = cache.save_to_cache(
        'TEST_DATASET',
        {'geo': 'EA19', 'test': 'value'},
        test_series
    )
    print(f"   Save: {'OK' if success else 'FAILED'}")
    
    # Test retrieve
    print("\n2. Retrieving from cache...")
    cached = cache.get_cached_data(
        'TEST_DATASET',
        {'geo': 'EA19', 'test': 'value'},
        max_age_hours=24
    )
    
    if cached is not None:
        print(f"   Retrieved: {len(cached)} observations")
        print(f"   Match: {'OK' if len(cached) == len(test_series) else 'FAILED'}")
    else:
        print("   FAILED to retrieve")
    
    # Test cache info
    print("\n3. Cache info:")
    info = cache.get_cache_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print("\n✓ Cache manager test complete\n")


if __name__ == "__main__":
    test_cache_manager()

