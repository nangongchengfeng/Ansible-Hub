// Mock API 数据
export const mockLogin = (data) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (data.username === 'admin' && data.password === 'admin123') {
        resolve({
          data: {
            access_token: 'mock-access-token-' + Date.now(),
            refresh_token: 'mock-refresh-token-' + Date.now(),
            token_type: 'Bearer'
          }
        })
      } else {
        reject({
          response: {
            status: 401,
            data: {
              message: '用户名或密码错误'
            }
          }
        })
      }
    }, 500)
  })
}

export const mockLogout = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: { message: '登出成功' } })
    }, 200)
  })
}

export const mockGetCurrentUser = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data: {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          role: 'superadmin',
          name: '超级管理员',
          created_at: '2024-01-01T00:00:00Z'
        }
      })
    }, 200)
  })
}

// Mock 业务节点数据
const mockBusinessNodes = [
  {
    id: 1,
    name: '集团总部',
    description: '总公司',
    parentId: null,
    gatewayId: null,
    permissions: { view: true, execute: true, manage: true },
    children: [
      {
        id: 2,
        name: '研发事业部',
        description: '负责产品研发',
        parentId: 1,
        gatewayId: 1,
        children: [
          { id: 4, name: '前端组', description: '前端开发团队', parentId: 2 },
          { id: 5, name: '后端组', description: '后端开发团队', parentId: 2 }
        ]
      },
      {
        id: 3,
        name: '测试事业部',
        description: '负责质量保证',
        parentId: 1,
        children: []
      }
    ]
  }
]

// Mock 网关数据
let mockGateways = [
  { id: 1, name: '北京网关', host: '10.0.0.1', port: 22 }
]

let gatewayNextId = 2

export const mockGetBusinessNodes = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockBusinessNodes })
    }, 300)
  })
}

export const mockGetGateways = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockGateways })
    }, 200)
  })
}

let nextId = 10

export const mockCreateBusinessNode = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newNode = {
        id: nextId++,
        name: data.name,
        description: data.description,
        parentId: data.parentId,
        gatewayId: data.gatewayId,
        children: []
      }

      // 把新节点加入树中
      if (data.parentId) {
        // 找到父节点并添加
        const addToParent = (nodes) => {
          for (const node of nodes) {
            if (node.id === data.parentId) {
              if (!node.children) node.children = []
              node.children.push(newNode)
              return true
            }
            if (node.children && addToParent(node.children)) return true
          }
          return false
        }
        addToParent(mockBusinessNodes)
      } else {
        // 根节点
        mockBusinessNodes.push(newNode)
      }

      resolve({ data: newNode })
    }, 300)
  })
}

export const mockUpdateBusinessNode = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 查找并更新节点
      const updateNode = (nodes) => {
        for (const node of nodes) {
          if (node.id === id) {
            node.name = data.name
            node.description = data.description
            node.gatewayId = data.gatewayId
            // 注意：这里不允许修改parentId，因为移动节点是单独的功能
            return true
          }
          if (node.children && updateNode(node.children)) return true
        }
        return false
      }

      updateNode(mockBusinessNodes)
      resolve({ data: { id, ...data } })
    }, 300)
  })
}

export const mockDeleteBusinessNode = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 删除节点
      const deleteNode = (nodes) => {
        for (let i = 0; i < nodes.length; i++) {
          const node = nodes[i]
          if (node.id === id) {
            nodes.splice(i, 1)
            return true
          }
          if (node.children && deleteNode(node.children)) return true
        }
        return false
      }

      deleteNode(mockBusinessNodes)
      resolve({ data: { success: true } })
    }, 300)
  })
}

export const mockUpdateNodePermissions = (id, permissions) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 查找并更新节点权限
      const updatePermissions = (nodes) => {
        for (const node of nodes) {
          if (node.id === id) {
            node.permissions = permissions
            return true
          }
          if (node.children && updatePermissions(node.children)) return true
        }
        return false
      }

      updatePermissions(mockBusinessNodes)
      resolve({ data: { id, permissions } })
    }, 300)
  })
}

// Mock 系统用户数据
let mockSystemUsers = [
  { id: 1, name: 'root', username: 'root', authType: 'password', password: '****', privateKey: null, createdBy: 'admin' },
  { id: 2, name: 'deploy', username: 'deploy', authType: 'key', password: null, privateKey: '-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----', createdBy: 'admin' }
]

let systemUserNextId = 3

// Mock 主机数据
let mockHosts = [
  { id: 1, name: 'Web Server 01', hostname: '192.168.1.10', port: 22, businessNodeId: 4, systemUserId: 1, gatewayId: 1, enabled: true, status: 'online' },
  { id: 2, name: 'Web Server 02', hostname: '192.168.1.11', port: 22, businessNodeId: 4, systemUserId: 2, gatewayId: 1, enabled: true, status: 'online' },
  { id: 3, name: 'DB Server 01', hostname: '192.168.1.20', port: 22, businessNodeId: 5, systemUserId: 1, gatewayId: 1, enabled: true, status: 'offline' },
  { id: 4, name: 'Test Server', hostname: '192.168.1.30', port: 22, businessNodeId: 3, systemUserId: 2, gatewayId: null, enabled: false, status: 'unknown' }
]

let hostNextId = 5

export const mockGetSystemUsers = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockSystemUsers })
    }, 200)
  })
}

export const mockGetHosts = (params) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filteredHosts = [...mockHosts]

      // 按业务节点筛选
      if (params?.businessNodeId) {
        filteredHosts = filteredHosts.filter(h => h.businessNodeId === params.businessNodeId)
      }

      resolve({
        data: filteredHosts,
        total: filteredHosts.length
      })
    }, 300)
  })
}

export const mockCreateHost = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newHost = {
        id: hostNextId++,
        ...data,
        enabled: true,
        status: 'unknown'
      }
      mockHosts.push(newHost)
      resolve({ data: newHost })
    }, 300)
  })
}

export const mockUpdateHost = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const host = mockHosts.find(h => h.id === id)
      if (host) {
        Object.assign(host, data)
      }
      resolve({ data: { id, ...data } })
    }, 300)
  })
}

export const mockDeleteHost = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockHosts = mockHosts.filter(h => h.id !== id)
      resolve({ data: { success: true } })
    }, 300)
  })
}

export const mockToggleHost = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const host = mockHosts.find(h => h.id === id)
      if (host) {
        host.enabled = !host.enabled
      }
      resolve({ data: { id, enabled: host?.enabled } })
    }, 200)
  })
}

export const mockCreateSystemUser = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newUser = {
        id: systemUserNextId++,
        ...data,
        createdBy: 'admin'
      }
      mockSystemUsers.push(newUser)
      resolve({ data: newUser })
    }, 300)
  })
}

export const mockUpdateSystemUser = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const user = mockSystemUsers.find(u => u.id === id)
      if (user) {
        Object.assign(user, data)
      }
      resolve({ data: { id, ...data } })
    }, 300)
  })
}

export const mockDeleteSystemUser = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockSystemUsers = mockSystemUsers.filter(u => u.id !== id)
      resolve({ data: { success: true } })
    }, 300)
  })
}

export const mockCreateGateway = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newGateway = {
        id: gatewayNextId++,
        ...data
      }
      mockGateways.push(newGateway)
      resolve({ data: newGateway })
    }, 300)
  })
}

export const mockUpdateGateway = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const gateway = mockGateways.find(g => g.id === id)
      if (gateway) {
        Object.assign(gateway, data)
      }
      resolve({ data: { id, ...data } })
    }, 300)
  })
}

export const mockDeleteGateway = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockGateways = mockGateways.filter(g => g.id !== id)
      resolve({ data: { success: true } })
    }, 300)
  })
}

// Mock 脚本数据
let mockScripts = [
  { id: 1, name: 'backup.sh', description: '系统备份脚本', content: '#!/bin/bash\n# Backup script\ntar -czf /backup/backup-$(date +%Y%m%d).tar.gz /data', currentVersion: 2, createdBy: 'admin', createdAt: '2024-01-01T00:00:00Z', updatedAt: '2024-01-05T00:00:00Z' },
  { id: 2, name: 'deploy.sh', description: '应用部署脚本', content: '#!/bin/bash\n# Deploy script\ncd /app && ./deploy.sh', currentVersion: 1, createdBy: 'admin', createdAt: '2024-01-02T00:00:00Z', updatedAt: '2024-01-02T00:00:00Z' }
]

let mockScriptVersions = {
  1: [
    { id: 'v1', scriptId: 1, version: 1, content: '#!/bin/bash\n# Backup script\ntar -czf /backup/backup-$(date +%Y%m%d).tar.gz /data', changeNote: '初始版本', createdBy: 'admin', createdAt: '2024-01-01T00:00:00Z' },
    { id: 'v2', scriptId: 1, version: 2, content: '#!/bin/bash\n# Backup script\ntar -czf /backup/backup-$(date +%Y%m%d).tar.gz /data\n# Added compression level\nGZIP=-9', changeNote: '添加压缩级别配置', createdBy: 'admin', createdAt: '2024-01-05T00:00:00Z' }
  ],
  2: [
    { id: 'v1', scriptId: 2, version: 1, content: '#!/bin/bash\n# Deploy script\ncd /app && ./deploy.sh', changeNote: '初始版本', createdBy: 'admin', createdAt: '2024-01-02T00:00:00Z' }
  ]
}

let scriptNextId = 3
let scriptVersionNextId = 3

export const mockGetScripts = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockScripts })
    }, 300)
  })
}

export const mockCreateScript = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newScript = {
        id: scriptNextId++,
        ...data,
        currentVersion: 1,
        createdBy: 'admin',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      mockScripts.push(newScript)

      // 创建初始版本
      mockScriptVersions[newScript.id] = [
        {
          id: `v${scriptVersionNextId++}`,
          scriptId: newScript.id,
          version: 1,
          content: data.content,
          changeNote: data.changeNote || '初始版本',
          createdBy: 'admin',
          createdAt: new Date().toISOString()
        }
      ]

      resolve({ data: newScript })
    }, 300)
  })
}

export const mockUpdateScript = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const script = mockScripts.find(s => s.id === id)
      if (script) {
        script.name = data.name
        script.description = data.description
        script.content = data.content
        script.updatedAt = new Date().toISOString()
        script.currentVersion++

        // 创建新版本
        const newVersion = {
          id: `v${scriptVersionNextId++}`,
          scriptId: id,
          version: script.currentVersion,
          content: data.content,
          changeNote: data.changeNote || '更新版本',
          createdBy: 'admin',
          createdAt: new Date().toISOString()
        }
        if (!mockScriptVersions[id]) {
          mockScriptVersions[id] = []
        }
        mockScriptVersions[id].push(newVersion)
      }
      resolve({ data: { id, ...data } })
    }, 300)
  })
}

export const mockDeleteScript = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockScripts = mockScripts.filter(s => s.id !== id)
      delete mockScriptVersions[id]
      resolve({ data: { success: true } })
    }, 300)
  })
}

export const mockGetScriptVersions = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockScriptVersions[id] || [] })
    }, 300)
  })
}

export const mockGetScriptVersion = (scriptId, versionId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const versions = mockScriptVersions[scriptId] || []
      const version = versions.find(v => v.id === versionId)
      resolve({ data: version })
    }, 300)
  })
}

export const mockRollbackScript = (scriptId, versionId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const script = mockScripts.find(s => s.id === scriptId)
      const versions = mockScriptVersions[scriptId] || []
      const targetVersion = versions.find(v => v.id === versionId)

      if (script && targetVersion) {
        script.content = targetVersion.content
        script.updatedAt = new Date().toISOString()
        script.currentVersion++

        // 创建回滚版本
        const newVersion = {
          id: `v${scriptVersionNextId++}`,
          scriptId: scriptId,
          version: script.currentVersion,
          content: targetVersion.content,
          changeNote: `回滚到版本 ${targetVersion.version}`,
          createdBy: 'admin',
          createdAt: new Date().toISOString()
        }
        versions.push(newVersion)
      }

      resolve({ data: { success: true } })
    }, 300)
  })
}

// Mock 剧本数据
let mockPlaybooks = [
  { id: 1, name: 'setup-webserver.yml', description: '部署 Web 服务器', content: '---\n- hosts: web_servers\n  roles:\n    - nginx', currentVersion: 2, createdBy: 'admin', createdAt: '2024-01-01T00:00:00Z', updatedAt: '2024-01-05T00:00:00Z' },
  { id: 2, name: 'deploy-app.yml', description: '部署应用程序', content: '---\n- hosts: app_servers\n  tasks:\n    - name: Deploy app\n      git: repo=https://github.com/app.git dest=/app', currentVersion: 1, createdBy: 'admin', createdAt: '2024-01-02T00:00:00Z', updatedAt: '2024-01-02T00:00:00Z' }
]

let mockPlaybookVersions = {
  1: [
    { id: 'v1', playbookId: 1, version: 1, content: '---\n- hosts: web_servers\n  roles:\n    - nginx', changeNote: '初始版本', createdBy: 'admin', createdAt: '2024-01-01T00:00:00Z' },
    { id: 'v2', playbookId: 1, version: 2, content: '---\n- hosts: web_servers\n  roles:\n    - nginx\n    - ssl', changeNote: '添加 SSL 配置', createdBy: 'admin', createdAt: '2024-01-05T00:00:00Z' }
  ],
  2: [
    { id: 'v1', playbookId: 2, version: 1, content: '---\n- hosts: app_servers\n  tasks:\n    - name: Deploy app\n      git: repo=https://github.com/app.git dest=/app', changeNote: '初始版本', createdBy: 'admin', createdAt: '2024-01-02T00:00:00Z' }
  ]
}

let playbookNextId = 3
let playbookVersionNextId = 3

export const mockGetPlaybooks = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockPlaybooks })
    }, 300)
  })
}

export const mockCreatePlaybook = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newPlaybook = {
        id: playbookNextId++,
        ...data,
        currentVersion: 1,
        createdBy: 'admin',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      mockPlaybooks.push(newPlaybook)

      mockPlaybookVersions[newPlaybook.id] = [
        {
          id: `v${playbookVersionNextId++}`,
          playbookId: newPlaybook.id,
          version: 1,
          content: data.content,
          changeNote: data.changeNote || '初始版本',
          createdBy: 'admin',
          createdAt: new Date().toISOString()
        }
      ]

      resolve({ data: newPlaybook })
    }, 300)
  })
}

export const mockUpdatePlaybook = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const playbook = mockPlaybooks.find(p => p.id === id)
      if (playbook) {
        playbook.name = data.name
        playbook.description = data.description
        playbook.content = data.content
        playbook.updatedAt = new Date().toISOString()
        playbook.currentVersion++

        const newVersion = {
          id: `v${playbookVersionNextId++}`,
          playbookId: id,
          version: playbook.currentVersion,
          content: data.content,
          changeNote: data.changeNote || '更新版本',
          createdBy: 'admin',
          createdAt: new Date().toISOString()
        }
        if (!mockPlaybookVersions[id]) {
          mockPlaybookVersions[id] = []
        }
        mockPlaybookVersions[id].push(newVersion)
      }
      resolve({ data: { id, ...data } })
    }, 300)
  })
}

export const mockDeletePlaybook = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockPlaybooks = mockPlaybooks.filter(p => p.id !== id)
      delete mockPlaybookVersions[id]
      resolve({ data: { success: true } })
    }, 300)
  })
}

export const mockGetPlaybookVersions = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockPlaybookVersions[id] || [] })
    }, 300)
  })
}

export const mockGetPlaybookVersion = (playbookId, versionId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const versions = mockPlaybookVersions[playbookId] || []
      const version = versions.find(v => v.id === versionId)
      resolve({ data: version })
    }, 300)
  })
}

export const mockRollbackPlaybook = (playbookId, versionId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const playbook = mockPlaybooks.find(p => p.id === playbookId)
      const versions = mockPlaybookVersions[playbookId] || []
      const targetVersion = versions.find(v => v.id === versionId)

      if (playbook && targetVersion) {
        playbook.content = targetVersion.content
        playbook.updatedAt = new Date().toISOString()
        playbook.currentVersion++

        const newVersion = {
          id: `v${playbookVersionNextId++}`,
          playbookId: playbookId,
          version: playbook.currentVersion,
          content: targetVersion.content,
          changeNote: `回滚到版本 ${targetVersion.version}`,
          createdBy: 'admin',
          createdAt: new Date().toISOString()
        }
        versions.push(newVersion)
      }

      resolve({ data: { success: true } })
    }, 300)
  })
}

// Mock 命令过滤规则数据
let mockCommandFilters = [
  { id: 1, name: '禁止 rm -rf', pattern: 'rm -rf', type: 'string', enabled: true, priority: 1, createdBy: 'admin', createdAt: '2024-01-01T00:00:00Z' },
  { id: 2, name: '禁止 dd 命令', pattern: 'dd\\s+if=', type: 'regex', enabled: true, priority: 2, createdBy: 'admin', createdAt: '2024-01-02T00:00:00Z' },
  { id: 3, name: '禁止格式化磁盘', pattern: 'mkfs\\.', type: 'regex', enabled: false, priority: 3, createdBy: 'admin', createdAt: '2024-01-03T00:00:00Z' }
]

let commandFilterNextId = 4

export const mockGetCommandFilters = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockCommandFilters })
    }, 300)
  })
}

export const mockCreateCommandFilter = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newFilter = {
        id: commandFilterNextId++,
        ...data,
        enabled: true,
        priority: mockCommandFilters.length + 1,
        createdBy: 'admin',
        createdAt: new Date().toISOString()
      }
      mockCommandFilters.push(newFilter)
      resolve({ data: newFilter })
    }, 300)
  })
}

export const mockUpdateCommandFilter = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const filter = mockCommandFilters.find(f => f.id === id)
      if (filter) {
        Object.assign(filter, data)
      }
      resolve({ data: { id, ...data } })
    }, 300)
  })
}

export const mockDeleteCommandFilter = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockCommandFilters = mockCommandFilters.filter(f => f.id !== id)
      mockCommandFilters.forEach((f, index) => {
        f.priority = index + 1
      })
      resolve({ data: { success: true } })
    }, 300)
  })
}

export const mockToggleCommandFilter = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const filter = mockCommandFilters.find(f => f.id === id)
      if (filter) {
        filter.enabled = !filter.enabled
      }
      resolve({ data: { id, enabled: filter?.enabled } })
    }, 200)
  })
}

export const mockMoveCommandFilter = (id, direction) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const index = mockCommandFilters.findIndex(f => f.id === id)
      if (index !== -1) {
        const filter = mockCommandFilters[index]
        if (direction === 'up' && index > 0) {
          mockCommandFilters.splice(index, 1)
          mockCommandFilters.splice(index - 1, 0, filter)
        } else if (direction === 'down' && index < mockCommandFilters.length - 1) {
          mockCommandFilters.splice(index, 1)
          mockCommandFilters.splice(index + 1, 0, filter)
        }
        mockCommandFilters.forEach((f, i) => {
          f.priority = i + 1
        })
      }
      resolve({ data: { success: true } })
    }, 300)
  })
}

export const mockCheckCommand = (command) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let blocked = false
      let message = '命令安全，可以执行'
      let ruleName = ''

      for (const filter of mockCommandFilters) {
        if (!filter.enabled) continue
        if (filter.type === 'string') {
          if (command.includes(filter.pattern)) {
            blocked = true
            message = `命令被禁止：${filter.name}`
            ruleName = filter.name
            break
          }
        } else if (filter.type === 'regex') {
          try {
            if (new RegExp(filter.pattern).test(command)) {
              blocked = true
              message = `命令被禁止：${filter.name}`
              ruleName = filter.name
              break
            }
          } catch (e) {}
        }
      }

      resolve({ data: { blocked, message, ruleName } })
    }, 200)
  })
}

let jobNextId = 1
export const mockExecuteJob = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const jobId = `job-${jobNextId++}`
      resolve({ data: { jobId, status: 'running' } })
    }, 300)
  })
}

export const mockCancelJob = (jobId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: { success: true, message: '作业已取消' } })
    }, 200)
  })
}

export const mockSaveTemplate = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: { templateId: `template-${Date.now()}`, name: data.name, success: true } })
    }, 300)
  })
}

// Mock 作业模板数据
let mockJobTemplates = [
  {
    id: 1,
    name: '日常备份作业',
    description: '每日自动备份数据',
    executeType: 'script',
    scriptId: 1,
    hostIds: [1, 2],
    cronExpression: '0 2 * * *',
    enabled: true,
    permissions: { view: true, execute: true, manage: true },
    createdBy: 'admin',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-05T00:00:00Z'
  },
  {
    id: 2,
    name: '服务重启作业',
    description: '每周重启服务',
    executeType: 'shell',
    command: 'systemctl restart myapp',
    hostIds: [1],
    cronExpression: '0 3 * * 0',
    enabled: false,
    permissions: { view: true, execute: false, manage: true },
    createdBy: 'admin',
    createdAt: '2024-01-02T00:00:00Z',
    updatedAt: '2024-01-02T00:00:00Z'
  }
]

let jobTemplateNextId = 3

export const mockGetJobTemplates = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockJobTemplates })
    }, 300)
  })
}

export const mockCreateJobTemplate = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newTemplate = {
        id: jobTemplateNextId++,
        ...data,
        enabled: true,
        permissions: { view: true, execute: true, manage: true },
        createdBy: 'admin',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      mockJobTemplates.push(newTemplate)
      resolve({ data: newTemplate })
    }, 300)
  })
}

export const mockUpdateJobTemplate = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const template = mockJobTemplates.find(t => t.id === id)
      if (template) {
        Object.assign(template, data, { updatedAt: new Date().toISOString() })
      }
      resolve({ data: { id, ...data } })
    }, 300)
  })
}

export const mockDeleteJobTemplate = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockJobTemplates = mockJobTemplates.filter(t => t.id !== id)
      resolve({ data: { success: true } })
    }, 300)
  })
}

export const mockToggleJobTemplate = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const template = mockJobTemplates.find(t => t.id === id)
      if (template) {
        template.enabled = !template.enabled
      }
      resolve({ data: { id, enabled: template?.enabled } })
    }, 200)
  })
}

export const mockTriggerJobTemplate = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: { jobId: `job-${Date.now()}`, success: true, message: '作业已触发' } })
    }, 500)
  })
}

export const mockUpdateTemplatePermissions = (id, permissions) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const template = mockJobTemplates.find(t => t.id === id)
      if (template) {
        template.permissions = permissions
      }
      resolve({ data: { id, permissions } })
    }, 300)
  })
}

// Mock 作业历史数据
let mockJobHistory = [
  {
    id: 1,
    name: '日常备份作业',
    executeType: 'script',
    status: 'success',
    hostNames: ['Web Server 01', 'Web Server 02'],
    startedAt: '2024-01-15T02:00:00Z',
    completedAt: '2024-01-15T02:15:30Z',
    duration: 930,
    createdBy: 'system'
  },
  {
    id: 2,
    name: '手动执行 - Shell命令',
    executeType: 'shell',
    status: 'success',
    hostNames: ['Web Server 01'],
    startedAt: '2024-01-14T10:30:00Z',
    completedAt: '2024-01-14T10:32:15Z',
    duration: 135,
    createdBy: 'admin'
  },
  {
    id: 3,
    name: '服务重启作业',
    executeType: 'shell',
    status: 'failed',
    hostNames: ['DB Server 01'],
    startedAt: '2024-01-13T03:00:00Z',
    completedAt: '2024-01-13T03:05:20Z',
    duration: 320,
    createdBy: 'system'
  },
  {
    id: 4,
    name: '部署应用',
    executeType: 'playbook',
    status: 'cancelled',
    hostNames: ['Web Server 01', 'Web Server 02'],
    startedAt: '2024-01-12T14:00:00Z',
    completedAt: '2024-01-12T14:10:00Z',
    duration: 600,
    createdBy: 'admin'
  },
  {
    id: 5,
    name: '正在运行的作业',
    executeType: 'shell',
    status: 'running',
    hostNames: ['Test Server'],
    startedAt: '2024-01-15T08:00:00Z',
    completedAt: null,
    duration: null,
    createdBy: 'admin'
  }
]

let jobHistoryNextId = 6

export const mockGetJobHistory = (params) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filtered = [...mockJobHistory]

      if (params?.status && params.status !== 'all') {
        filtered = filtered.filter(j => j.status === params.status)
      }

      if (params?.startTime) {
        filtered = filtered.filter(j => new Date(j.startedAt) >= new Date(params.startTime))
      }

      if (params?.endTime) {
        filtered = filtered.filter(j => new Date(j.startedAt) <= new Date(params.endTime))
      }

      resolve({ data: filtered, total: filtered.length })
    }, 300)
  })
}

export const mockGetJobDetail = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const job = mockJobHistory.find(j => j.id === id)
      resolve({ data: job })
    }, 300)
  })
}

export const mockGetJobLogs = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const logs = [
        { time: '2024-01-15T02:00:00Z', level: 'info', message: '开始执行作业' },
        { time: '2024-01-15T02:00:05Z', level: 'info', message: '连接主机 Web Server 01' },
        { time: '2024-01-15T02:00:10Z', level: 'info', message: '上传执行文件' },
        { time: '2024-01-15T02:00:30Z', level: 'info', message: '开始执行脚本' },
        { time: '2024-01-15T02:10:00Z', level: 'info', message: '执行进度: 50%' },
        { time: '2024-01-15T02:15:00Z', level: 'info', message: '执行进度: 100%' },
        { time: '2024-01-15T02:15:30Z', level: 'success', message: '作业执行完成' }
      ]
      resolve({ data: logs })
    }, 300)
  })
}

export const mockRedoJob = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const originalJob = mockJobHistory.find(j => j.id === id)
      const newJob = {
        id: jobHistoryNextId++,
        name: `重做 - ${originalJob?.name}`,
        executeType: originalJob?.executeType || 'shell',
        status: 'running',
        hostNames: originalJob?.hostNames || [],
        startedAt: new Date().toISOString(),
        completedAt: null,
        duration: null,
        createdBy: 'admin'
      }
      mockJobHistory.unshift(newJob)
      resolve({ data: { jobId: newJob.id, success: true, message: '作业已重新执行' } })
    }, 500)
  })
}

export const mockGetDashboardData = (params) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const now = new Date()
      const days = 7

      // 作业成功率趋势
      const successRate = []
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now)
        date.setDate(date.getDate() - i)
        successRate.push({
          date: date.toISOString().split('T')[0],
          rate: Number((85 + Math.random() * 15).toFixed(1))
        })
      }

      // 失败率 Top 10
      const topFailed = [
        { name: 'DB Server重启', count: 23, rate: 35 },
        { name: '应用部署脚本', count: 18, rate: 28 },
        { name: '数据备份', count: 15, rate: 22 },
        { name: '系统更新', count: 12, rate: 18 },
        { name: '配置同步', count: 10, rate: 15 }
      ]

      // 执行最耗时的作业
      const longestDuration = [
        { name: '全量备份作业', duration: 1800 },
        { name: '数据库迁移', duration: 1200 },
        { name: '系统升级', duration: 900 },
        { name: '应用部署', duration: 600 },
        { name: '环境初始化', duration: 450 }
      ]

      // 最常被执行的剧本
      const mostExecuted = [
        { name: 'web服务器配置', count: 156 },
        { name: '应用部署', count: 123 },
        { name: '环境检查', count: 89 },
        { name: '数据库备份', count: 78 },
        { name: '系统更新', count: 65 }
      ]

      const data = {
        stats: {
          totalJobs: 1234,
          successRate: 92.5,
          avgDuration: 345,
          automationCoverage: 78
        },
        successRate,
        topFailed,
        longestDuration,
        mostExecuted
      }

      resolve({ data })
    }, 300)
  })
}

// Mock 审计日志数据
let mockAuditLogs = [
  { id: 1, action: 'LOGIN', user: 'admin', detail: '用户登录系统', ip: '192.168.1.1', createdAt: '2024-01-15T10:30:00Z' },
  { id: 2, action: 'CREATE', user: 'admin', detail: '创建业务节点「测试环境」', ip: '192.168.1.1', createdAt: '2024-01-15T10:35:00Z' },
  { id: 3, action: 'UPDATE', user: 'admin', detail: '更新主机「Web Server 01」配置', ip: '192.168.1.1', createdAt: '2024-01-15T10:40:00Z' },
  { id: 4, action: 'DELETE', user: 'admin', detail: '删除旧脚本「test.sh」', ip: '192.168.1.1', createdAt: '2024-01-15T10:45:00Z' },
  { id: 5, action: 'EXECUTE', user: 'admin', detail: '执行作业「日常备份」', ip: '192.168.1.1', createdAt: '2024-01-15T11:00:00Z' },
  { id: 6, action: 'LOGIN', user: 'auditor', detail: '用户登录系统', ip: '192.168.1.2', createdAt: '2024-01-15T11:30:00Z' },
  { id: 7, action: 'PERMISSION', user: 'admin', detail: '修改用户「operator」权限', ip: '192.168.1.1', createdAt: '2024-01-15T12:00:00Z' },
  { id: 8, action: 'LOGOUT', user: 'auditor', detail: '用户退出系统', ip: '192.168.1.2', createdAt: '2024-01-15T12:30:00Z' }
]

export const mockGetAuditLogs = (params) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filtered = [...mockAuditLogs]

      if (params?.action && params?.action !== 'all') {
        filtered = filtered.filter(log => log.action === params.action)
      }

      if (params?.user && params?.user !== 'all') {
        filtered = filtered.filter(log => log.user === params.user)
      }

      if (params?.startTime) {
        filtered = filtered.filter(log => new Date(log.createdAt) >= new Date(params.startTime))
      }

      if (params?.endTime) {
        filtered = filtered.filter(log => new Date(log.createdAt) <= new Date(params.endTime))
      }

      filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))

      resolve({ data: filtered, total: filtered.length })
    }, 300)
  })
}

export const mockGetAuditLogDetail = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const log = mockAuditLogs.find(l => l.id === id)
      resolve({ data: log })
    }, 300)
  })
}

// Mock 用户数据
let mockUsers = [
  {
    id: 1,
    username: 'admin',
    name: '超级管理员',
    email: 'admin@example.com',
    role: 'superadmin',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    username: 'auditor',
    name: '审计员',
    email: 'auditor@example.com',
    role: 'auditor',
    createdAt: '2024-01-05T00:00:00Z',
    updatedAt: '2024-01-05T00:00:00Z'
  },
  {
    id: 3,
    username: 'operator',
    name: '操作员',
    email: 'operator@example.com',
    role: 'operator',
    createdAt: '2024-01-10T00:00:00Z',
    updatedAt: '2024-01-10T00:00:00Z'
  }
]

let userNextId = 4

export const mockGetUsers = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockUsers, total: mockUsers.length })
    }, 300)
  })
}

export const mockCreateUser = (data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newUser = {
        id: userNextId++,
        ...data,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      mockUsers.push(newUser)
      resolve({ data: newUser })
    }, 300)
  })
}

export const mockUpdateUser = (id, data) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const user = mockUsers.find(u => u.id === id)
      if (user) {
        Object.assign(user, data, { updatedAt: new Date().toISOString() })
      }
      resolve({ data: { id, ...data } })
    }, 300)
  })
}

export const mockDeleteUser = (id) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockUsers = mockUsers.filter(u => u.id !== id)
      resolve({ data: { success: true } })
    }, 300)
  })
}

export const mockResetUserPassword = (id, newPassword) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: { success: true, message: '密码已重置' } })
    }, 300)
  })
}
