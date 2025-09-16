# Boss直聘数据仪表盘

这是一个基于Flask的Web仪表盘，用于可视化分析Boss直聘爬虫抓取的职位数据，支持自定义SQL查询功能。

## 功能特性

### 📊 数据可视化
- **统计卡片**: 显示总职位数、覆盖省份、行业类型、企业数量等关键指标
- **图表展示**: 
  - 省份职位分布（柱状图）
  - 行业分布（环形图）
  - 薪资范围分布（横向柱状图）
  - 学历要求分布（饼图）

### 🔍 自定义SQL查询
- **安全查询**: 只允许SELECT语句，防止数据被误操作
- **实时执行**: 支持自定义SQL语句实时查询数据
- **查询示例**: 提供常用的查询模板
- **结果展示**: 以表格形式展示查询结果

### 🛡️ 安全特性
- SQL注入防护
- 只允许查询操作，禁止增删改操作
- 输入验证和错误处理

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 确保数据库运行
确保MySQL服务已启动，并且数据库`spider_db`和表`job_info`已创建。

### 3. 启动仪表盘
```bash
python start_dashboard.py
```

或者直接运行Flask应用：
```bash
python dashboard_app.py
```

### 4. 访问仪表盘
打开浏览器访问: http://localhost:5000

## API接口

### 获取仪表盘统计数据
```
GET /api/dashboard/stats
```

### 执行SQL查询
```
POST /api/sql/query
Content-Type: application/json

{
    "sql": "SELECT job_title, job_company FROM job_info LIMIT 10"
}
```

### 获取表信息
```
GET /api/sql/tables
```

### 获取SQL示例
```
GET /api/sql/examples
```

## SQL查询示例

### 1. 查询各城市职位数量
```sql
SELECT job_location, COUNT(*) as count 
FROM job_info 
GROUP BY job_location 
ORDER BY count DESC 
LIMIT 20
```

### 2. 查询高薪职位（20K以上）
```sql
SELECT job_title, job_company, job_salary_range, job_location 
FROM job_info 
WHERE job_salary_range LIKE '%20%' 
   OR job_salary_range LIKE '%30%' 
   OR job_salary_range LIKE '%40%' 
   OR job_salary_range LIKE '%50%' 
LIMIT 20
```

### 3. 查询大厂职位
```sql
SELECT job_title, job_company, job_salary_range, job_location 
FROM job_info 
WHERE job_company IN ('腾讯', '阿里巴巴', '百度', '字节跳动', '美团', '滴滴', '京东', '网易') 
LIMIT 20
```

### 4. 查询Python相关职位
```sql
SELECT job_title, job_company, job_salary_range, job_location 
FROM job_info 
WHERE job_title LIKE '%Python%' 
   OR job_skills LIKE '%Python%' 
LIMIT 20
```

### 5. 统计各学历要求的职位数量
```sql
SELECT job_education, COUNT(*) as count 
FROM job_info 
WHERE job_education IS NOT NULL 
GROUP BY job_education 
ORDER BY count DESC
```

## 数据库表结构

表名: `job_info`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| category | varchar(255) | 一级分类 |
| sub_category | varchar(255) | 二级分类 |
| job_title | varchar(255) | 岗位名称 |
| province | varchar(100) | 省份 |
| job_location | varchar(255) | 工作位置 |
| job_company | varchar(255) | 企业名称 |
| job_industry | varchar(255) | 行业类型 |
| job_finance | varchar(255) | 融资情况 |
| job_scale | varchar(255) | 企业规模 |
| job_welfare | varchar(255) | 企业福利 |
| job_salary_range | varchar(255) | 薪资范围 |
| job_experience | varchar(255) | 工作年限 |
| job_education | varchar(255) | 学历要求 |
| job_skills | varchar(255) | 技能要求 |
| create_time | varchar(50) | 抓取时间 |

## 技术栈

- **后端**: Flask + PyMySQL
- **前端**: HTML5 + CSS3 + JavaScript
- **图表库**: Chart.js
- **数据库**: MySQL

## 注意事项

1. 确保数据库连接配置正确（在`dashboard_app.py`中修改DB_CONFIG）
2. 只支持SELECT查询语句，其他操作会被拒绝
3. 建议在生产环境中修改默认端口和添加认证机制
4. 大量数据查询时注意性能优化

## 故障排除

### 常见问题

1. **ImportError: No module named 'flask_cors'**
   ```bash
   pip install Flask-CORS
   ```

2. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库配置信息
   - 确认数据库和表是否存在

3. **端口被占用**
   - 修改`dashboard_app.py`中的端口号
   - 或者停止占用5000端口的其他服务

## 更新日志

- v1.0.0: 初始版本，支持基础数据可视化和SQL查询功能
