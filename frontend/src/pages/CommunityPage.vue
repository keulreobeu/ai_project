<!--Community Page-->
<template>
  <div class="community-page">
    <div class="community-header">
      <h1>익명 커뮤니티</h1>
      <p>축제와 서울 정보에 대해 자유롭게 이야기해보세요</p>
    </div>

    <div class="community-container">
      <div class="category-tabs">
        <button
          v-for="cat in categories"
          :key="cat.id"
          :class="['category-tab', { active: selectedCategory === cat.id }]"
          @click="selectedCategory = cat.id"
        >
          {{ cat.label }}
        </button>
      </div>

      <div class="community-actions">
        <div class="search-box">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="제목으로 검색..."
            @keyup.enter="loadPosts"
          />
          <button @click="loadPosts" class="search-btn">검색</button>
        </div>
        <button @click="showPostForm = true" class="btn-write">
          <span>✏️</span> 새 글쓰기
        </button>
      </div>

      <div class="posts-list">
        <div v-if="loading" class="loading-state">
          <p>로딩 중...</p>
        </div>
        <div v-else-if="filteredPosts.length === 0" class="empty-state">
          <p>게시글이 없습니다. 첫 번째 글을 작성해보세요!</p>
        </div>
        <div v-else class="posts-container">
          <CommunityPostCard
            v-for="post in filteredPosts"
            :key="post.post_id"
            :post="post"
            @click="viewPostDetail(post.post_id)"
          />
        </div>
      </div>
    </div>

    <div v-if="showPostForm" class="modal-overlay" @click.self="closePostForm">
      <div class="modal-content">
        <button class="modal-close" @click="closePostForm">✕</button>
        <CommunityPostForm
          @submit="handlePostSubmit"
          @cancel="closePostForm"
        />
      </div>
    </div>

    <div v-if="showPostDetail" class="modal-overlay" @click.self="closePostDetail">
      <div class="modal-content modal-large">
        <CommunityPostDetail
          v-if="selectedPost"
          :post="selectedPost"
          @close="closePostDetail"
          @edit="handleEditPost"
          @delete="handleDeletePost"
        />
      </div>
    </div>

    <div v-if="showEditForm" class="modal-overlay" @click.self="closeEditForm">
      <div class="modal-content">
        <button class="modal-close" @click="closeEditForm">✕</button>
        <CommunityPostEditForm
          v-if="currentPost"
          :post="currentPost"
          @submit="handleEditSubmit"
          @cancel="closeEditForm"
        />
      </div>
    </div>

    <div v-if="notification" :class="['notification', notification.type]">
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
import CommunityPostCard from '../components/CommunityPostCard.vue';
import CommunityPostForm from '../components/CommunityPostForm.vue';
import CommunityPostDetail from '../components/CommunityPostDetail.vue';
import CommunityPostEditForm from '../components/CommunityPostEditForm.vue';
import { deletePost as deletePostRequest } from '../api/posts';

export default {
  name: 'CommunityPage',
  components: {
    CommunityPostCard,
    CommunityPostForm,
    CommunityPostDetail,
    CommunityPostEditForm,
  },
  data() {
    return {
      selectedCategory: 'general',
      categories: [
        { id: 'general', label: '자유게시판' },
        { id: 'festival', label: '축제' },
        { id: 'restaurant', label: '음식점' },
        { id: 'tips', label: '팁&정보' },
      ],
      posts: [],
      searchKeyword: '',
      loading: false,
      showPostForm: false,
      showPostDetail: false,
      showEditForm: false,
      selectedPost: null,
      currentPost: null,
      notification: null,
    };
  },
  computed: {
    filteredPosts() {
      if (!this.searchKeyword) return this.posts;
      return this.posts.filter(post =>
        post.title?.toLowerCase().includes(this.searchKeyword.toLowerCase())
      );
    },
  },
  watch: {
    selectedCategory() {
      this.loadPosts();
    },
  },
  mounted() {
    this.loadPosts();
  },
  methods: {
    async loadPosts() {
      this.loading = true;
      try {
        const response = await fetch(`/api/community/posts?category=${this.selectedCategory}`);
        const data = await response.json();
        this.posts = Array.isArray(data) ? data : (data.posts ?? []);
      } catch (error) {
        console.error('Failed to load posts:', error);
        this.showNotification('게시글 로드 실패', 'error');
      } finally {
        this.loading = false;
      }
    },

    async viewPostDetail(postId) {
      try {
        const response = await fetch(`/api/community/posts/${postId}`);
        if (!response.ok) throw new Error('Post not found');
        const data = await response.json();
        this.selectedPost = data.post ?? data;
        this.showPostDetail = true;
      } catch (error) {
        console.error('Failed to load post detail:', error);
        this.showNotification('게시글 로드 실패', 'error');
      }
    },

    async handlePostSubmit(postData) {
      try {
        const response = await fetch('/api/community/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(postData),
        });
        if (!response.ok) throw new Error('Failed to create post');
        this.showNotification('게시글이 작성되었습니다', 'success');
        this.closePostForm();
        this.selectedCategory = postData.category;
        this.loadPosts();
      } catch (error) {
        console.error('Failed to create post:', error);
        this.showNotification('게시글 작성 실패', 'error');
      }
    },

    handleEditPost(postId,password) {
      
      this.currentPost = {
        ...this.selectedPost,
        password
      };
      
      this.showPostDetail = false;
      this.showEditForm = true;
    },

    async handleEditSubmit(postId, editData) {
      try {
        const response = await fetch(`/api/community/posts/${postId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(editData),
        });
        
        // 💡 만약 비밀번호가 틀렸다면 백엔드가 401(invalid password) 또는 422를 보냅니다.
        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('비밀번호가 올바르지 않습니다.');
          }
          throw new Error('게시글 수정에 실패했습니다.');
        }
        
        this.showNotification('게시글이 수정되었습니다', 'success');
        this.closeEditForm();
        this.loadPosts();
      } catch (error) {
        console.error('Failed to update post:', error);
        // 💡 에러 메시지를 alert나 알림창으로 띄워 사용자에게 유용한 정보를 제공합니다.
        alert(error.message);
        this.showNotification(error.message, 'error');
      }
    },
    async handleDeletePost(postId, password) {
      try {
        await deletePostRequest(postId, password);
        this.showNotification('게시글이 삭제되었습니다', 'success');
        this.closePostDetail();
        this.loadPosts();
      } catch (error) {
        console.error('Failed to delete post:', error);
        const message = error.status === 401
          ? '비밀번호가 올바르지 않습니다.'
          : '게시글 삭제에 실패했습니다.';
        alert(message);
        this.showNotification(message, 'error');
      }
    },
    
    
    closePostForm() {
      this.showPostForm = false;
    },
    closePostDetail() {
      this.showPostDetail = false;
      this.selectedPost = null;
    },
    closeEditForm() {
      this.showEditForm = false;
      this.currentPost = null;
    },
    showNotification(message, type = 'info') {
      this.notification = { message, type };
      setTimeout(() => {
        this.notification = null;
      }, 3000);
    },
  },
};
</script>

<style scoped>
.community-page {
  min-height: 100vh;
  background-color: #f8fafc;
  width: 100%;
  padding: 24px 0;
}
.community-header {
  text-align: left;
  margin-bottom: 40px;
}
.community-header h1 {
  font-size: 42px;
  font-weight: 700;
  color: #222222;
  margin-bottom: 8px;
}
.community-header p {
  font-size: 16px;
  color: #6b7280;
}
.community-container {
  width: 100%;
  max-width: none;
  margin: 0;
}
.category-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  border-bottom: 2px solid #e5e7eb;
  flex-wrap: wrap;
}
.category-tab {
  padding: 12px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 15px;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: -2px;
}
.category-tab:hover {
  color: #00aeef;
}
.category-tab.active {
  color: #00aeef;
  border-bottom-color: #00aeef;
}
.community-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  align-items: center;
}
.search-box {
  flex: 1;
  display: flex;
  gap: 8px;
  min-width: 250px;
}
.search-box input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  background-color: #ffffff;
  color: #222222;
}
.search-box input:focus {
  outline: none;
  border-color: #00aeef;
  box-shadow: 0 0 0 3px rgba(0, 174, 239, 0.1);
}
.search-btn {
  padding: 10px 20px;
  background-color: #00aeef;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-write {
  padding: 10px 24px;
  background-color: #ff6b35;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}
.posts-list {
  min-height: 300px;
}
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
  font-size: 16px;
}
.posts-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}
.modal-content {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}
.modal-content.modal-large {
  max-width: 700px;
}
.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  z-index: 10;
}
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 16px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  z-index: 2000;
}
.notification.success { background-color: #7ac943; color: white; }
.notification.error { background-color: #ef4444; color: white; }
.notification.info { background-color: #00aeef; color: white; }
</style>
