<template>
  <div class="dashboard">
    <!-- 时间范围选择器 -->
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true" :model="timeRange">
        <el-form-item label="时间范围">
          <el-select v-model="timeRange.type" placeholder="请选择" @change="handleTimeRangeChange">
            <el-option label="今天" value="today" />
            <el-option label="本周" value="week" />
            <el-option label="本月" value="month" />
            <el-option label="最近7天" value="7days" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="timeRange.type === 'custom'">
          <el-date-picker
            v-model="timeRange.range"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            @change="fetchData"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">刷新数据</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon job-icon">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ dashboardData?.stats?.totalJobs || 0 }}</div>
              <div class="stat-label">总作业数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ (dashboardData?.stats?.successRate || 0).toFixed(1) }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon time-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatDuration(dashboardData?.stats?.avgDuration || 0) }}</div>
              <div class="stat-label">平均耗时</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon coverage-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ (dashboardData?.stats?.automationCoverage || 0).toFixed(1) }}%</div>
              <div class="stat-label">自动化覆盖率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <!-- 作业成功率趋势 -->
      <el-col :span="16">
        <el-card shadow="hover" style="margin-bottom: 20px">
          <template #header>
            <div class="card-header">
              <span>作业成功率趋势</span>
            </div>
          </template>
          <div class="chart-placeholder">
            <el-table :data="dashboardData?.successRate || []" style="width: 100%">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="rate" label="成功率">
                <template #default="{ row }">
                  <el-progress :percentage="row.rate" :stroke-width="20" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>

      <!-- 自动化覆盖率 -->
      <el-col :span="8">
        <el-card shadow="hover" style="margin-bottom: 20px">
          <template #header>
            <div class="card-header">
              <span>自动化覆盖主机比例</span>
            </div>
          </template>
          <div class="chart-placeholder" style="display: flex; justify-content: center; align-items: center; height: 300px">
            <el-progress
              type="dashboard"
              :percentage="dashboardData?.stats?.automationCoverage || 0"
              :stroke-width="15"
              style="flex: 1"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据表格 -->
    <el-row :gutter="20">
      <!-- 失败率 Top 10 -->
      <el-col :span="12">
        <el-card shadow="hover" style="margin-bottom: 20px">
          <template #header>
            <div class="card-header">
              <span>失败率 Top 10</span>
            </div>
          </template>
          <el-table :data="dashboardData?.topFailed || []" stripe>
            <el-table-column prop="name" label="作业名称" />
            <el-table-column prop="count" label="失败次数" width="100" sortable />
            <el-table-column prop="rate" label="失败率" width="120">
              <template #default="{ row }">
                <el-tag type="danger">{{ row.rate }}%</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 最常被执行的剧本 -->
      <el-col :span="12">
        <el-card shadow="hover" style="margin-bottom: 20px">
          <template #header>
            <div class="card-header">
              <span>最常被执行的剧本</span>
            </div>
          </template>
          <el-table :data="dashboardData?.mostExecuted || []" stripe>
            <el-table-column prop="name" label="剧本名称" />
            <el-table-column prop="count" label="执行次数" width="120" sortable />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 执行最耗时的作业 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>执行最耗时的作业</span>
            </div>
          </template>
          <el-table :data="dashboardData?.longestDuration || []" stripe>
            <el-table-column prop="name" label="作业名称" />
            <el-table-column prop="duration" label="耗时" width="150" sortable>
              <template #default="{ row }">
                {{ formatDuration(row.duration) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Monitor, Document, VideoPlay, CircleCheck, Clock } from '@element-plus/icons-vue'
import { getDashboardData } from '@/api/dashboard'

const loading = ref(false)
const dashboardData = ref(null)

const timeRange = reactive({
  type: '7days',
  range: null
})

const formatDuration = (seconds) => {
  if (!seconds) return '0秒'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (mins > 0) {
    return `${mins}分${secs}秒`
  }
  return `${secs}秒`
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      timeRange: timeRange.type,
      start: timeRange.range?.[0],
      end: timeRange.range?.[1]
    }
    const res = await getDashboardData(params)
    dashboardData.value = res.data
  } catch (error) {
    ElMessage.error('获取仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

const handleTimeRangeChange = () => {
  if (timeRange.type !== 'custom') {
    fetchData()
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 30px;
  color: white;
}

.job-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.success-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.time-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.coverage-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  min-height: 200px;
}
</style>
