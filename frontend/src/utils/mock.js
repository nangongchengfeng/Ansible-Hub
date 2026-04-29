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
const mockGateways = [
  { id: 1, name: '北京网关', host: '10.0.0.1', port: 22 }
]

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
