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
