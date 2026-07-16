<!--Community Post Detail-->
<template>
  <div class="post-detail">
    <div class="detail-header">
      <div class="header-info">
        <div class="title-row">
          <h1 class="detail-title">{{ post.title }}</h1>
          <button @click="$emit('close')" class="btn-back">✕</button>
        </div>

        <div class="detail-meta-row">
          <div class="detail-meta">
            <span class="category-badge">{{ getCategoryLabel(post.category) }}</span>
            <!-- 💡 작성일: 년.월.일 시:분 전체 노출 -->
            <span class="meta-item">작성: {{ formatDateTime(post.created_at) }}</span>
            <!-- 💡 수정된 경우에만 수정일(년.월.일 시:분)이 노출됩니다 -->
            <span v-if="isEdited" class="meta-item">수정: {{ formatDateTime(post.updated_at) }}</span>
            <span class="meta-item">조회수: {{ post.view_count ?? 0 }}</span>
          </div>

          <div class="header-actions">
            <button @click="toggleMenu" class="btn-menu">⋯</button>
            <div v-if="showEditOptions" class="edit-options">
              <button @click="openEditPasswordModal" class="option-btn edit" title="수정">✏️</button>
              <button @click="openDeletePasswordModal" class="option-btn delete" title="삭제">🗑️</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="detail-content">
      {{ post.content }}
    </div>

    <div
      v-if="showEditPasswordConfirm"
      class="delete-confirm"
      @click.self="closeEditPasswordModal"
    >
      <div class="confirm-box">
        <p class="confirm-title">수정하시겠습니까?</p>
        <p class="confirm-hint">비밀번호를 입력해주세요</p>

        <input
          v-model="editPassword"
          type="password"
          placeholder="비밀번호를 입력하세요"
          class="password-input"
          @keyup.enter="confirmEditPassword"
        />
        <p v-if="editError" class="error-text">{{ editError }}</p>

        <div class="confirm-actions">
          <button @click="confirmEditPassword" class="btn-confirm primary">확인</button>
          <button @click="closeEditPasswordModal" class="btn-confirm cancel">취소</button>
        </div>
      </div>
    </div>

    <div
      v-if="showDeleteConfirm"
      class="delete-confirm"
      @click.self="closeDeletePasswordModal"
    >
      <div class="confirm-box">
        <p class="confirm-title">게시글을 삭제하시겠습니까?</p>
        <p class="confirm-hint">비밀번호를 입력해주세요</p>

        <input
          v-model="deletePassword"
          type="password"
          placeholder="비밀번호를 입력하세요"
          class="password-input"
          @keyup.enter="confirmDelete"
        />
        <p v-if="deleteError" class="error-text">{{ deleteError }}</p>
        <div class="confirm-actions">
          <button @click="confirmDelete" class="btn-confirm delete">삭제</button>
          <button @click="closeDeletePasswordModal" class="btn-confirm cancel">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { verifyPostPassword } from '../api/posts';

export default {
  name: 'CommunityPostDetail',
  props: {
    post: {
      type: Object,
      required: true,
    },
  },
  emits: ['edit', 'delete', 'close'],
  data() {
    return {
      showEditOptions: false,
      showDeleteConfirm: false,
      showEditPasswordConfirm: false,
      deletePassword: '',
      editPassword: '',
      editError: '',
      deleteError: '',
    };
  },
  computed: {
    isEdited() {
      return !!this.post.updated_at && this.post.updated_at !== 0;
    },
  },
  methods: {
    toggleMenu() {
      this.showEditOptions = !this.showEditOptions;
    },
    openEditPasswordModal() {
      this.showEditOptions = false;
      this.showEditPasswordConfirm = true;
      this.editPassword = '';
      this.editError = '';
    },
    closeEditPasswordModal() {
      this.showEditPasswordConfirm = false;
      this.editPassword = '';
      this.editError = '';
    },
    openDeletePasswordModal() {
      this.showEditOptions = false;
      this.showDeleteConfirm = true;
      this.deletePassword = '';
      this.deleteError = '';
    },
    closeDeletePasswordModal() {
      this.showDeleteConfirm = false;
      this.deletePassword = '';
      this.deleteError = '';
    },
    formatDateTime(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      const today = new Date();
      if (date.toDateString() === today.toDateString()) {
        return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
      }
      return date.toLocaleDateString('ko-KR', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    },
    getCategoryLabel(categoryId) {
      const categories = {
        general: '자유게시판',
        festival: '축제',
        restaurant: '음식점',
        tips: '팁 & 정보',
      };
      return categories[categoryId] || categoryId;
    },
    async confirmEditPassword() {
      const enteredPassword = this.editPassword.trim();
      if (!enteredPassword) {
        this.editError = '비밀번호를 입력해주세요.';
        return;
      }
      try {
        const result = await verifyPostPassword(this.post.post_id, enteredPassword);

        if (!result.valid) {
          alert("비밀번호를 다시 확인해주세요.");
          return;
        }

        this.closeEditPasswordModal();
        // 💡 부모 컴포넌트로 'edit' 이벤트를 보낼 때, 검증이 끝난 비밀번호(enteredPassword)도 인자로 보냅니다.
        this.$emit('edit', this.post.post_id, enteredPassword);
      } catch (error) {
        this.editError = error.message || '비밀번호 확인 중 오류가 발생했습니다.';
      }
    },
    async confirmDelete() {
      const enteredPassword = this.deletePassword.trim();
      if (!enteredPassword) {
        this.deleteError = '비밀번호를 입력해주세요.';
        return;
      }
      try {
        const result = await verifyPostPassword(this.post.post_id, enteredPassword);
        if (!result.valid) {
          alert("비밀번호를 다시 확인해주세요.");
          return;
        }
        this.closeDeletePasswordModal();
        this.$emit('delete', this.post.post_id, enteredPassword);
      } catch (error) {
        this.deleteError = error.message || '비밀번호 확인 중 오류가 발생했습니다.';
      }
    },
  },
};
</script>

<style scoped>
.post-detail { padding: 24px; }
.detail-header { margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #e5e7eb; }
.header-info { display: flex; flex-direction: column; gap: 12px; }
.title-row { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.detail-title { font-size: 28px; font-weight: 700; color: #222222; margin: 0; line-height: 1.3; word-break: break-word; }
.detail-meta-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.detail-meta { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; font-size: 13px; color: #6b7280; }
.category-badge {
  display: inline-block;
  padding: 4px 8px;
  background-color: #00aeef;
  color: white;
  border-radius: 4px;
  font-weight: 600;
}
.meta-item { display: inline-block; }
.header-actions { position: relative; flex-shrink: 0; }
.btn-menu {
  background: none; border: none; font-size: 20px; cursor: pointer;
  color: #6b7280; padding: 4px 8px;
}
.btn-menu:hover { color: #222222; }
.edit-options {
  position: absolute; top: 100%; right: 0; background-color: #ffffff;
  border: 1px solid #e5e7eb; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 10; display: flex; gap: 4px; padding: 4px;
}
.option-btn {
  display: flex; align-items: center; justify-content: center; width: 36px; height: 36px;
  background: none; border: none; font-size: 18px; cursor: pointer; border-radius: 4px;
}
.option-btn:hover { background-color: #f3f4f6; }
.option-btn.delete:hover { background-color: #fee2e2; }
.detail-content { font-size: 15px; line-height: 1.8; color: #222222; white-space: pre-wrap; word-break: break-word; margin-bottom: 24px; }
.delete-confirm {
  position: fixed; inset: 0; background-color: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 2000; padding: 20px;
}
.confirm-box {
  background-color: #ffffff; border-radius: 12px; padding: 24px;
  max-width: 400px; width: 100%; text-align: center;
}
.confirm-box p { margin: 0 0 8px 0; font-size: 16px; color: #222222; }
.confirm-title { font-size: 18px; font-weight: 700; }
.confirm-hint { font-size: 14px; color: #6b7280; margin-bottom: 16px; }
.password-input {
  width: 100%; padding: 10px 12px; border: 1px solid #e5e7eb; border-radius: 6px;
  font-size: 14px; margin-bottom: 12px; box-sizing: border-box;
}
.password-input:focus { outline: none; border-color: #00aeef; box-shadow: 0 0 0 3px rgba(0,174,239,0.1); }
.error-text { color: #ef4444; font-size: 13px; margin-bottom: 12px; }
.confirm-actions { display: flex; gap: 8px; }
.btn-confirm { flex: 1; padding: 10px 12px; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-confirm.primary { background-color: #00aeef; color: white; }
.btn-confirm.delete { background-color: #ef4444; color: white; }
.btn-confirm.cancel { background-color: #e5e7eb; color: #222222; }
.btn-back {
  padding: 8px 14px; color: #222222; border: none; border-radius: 6px; font-size: 22px; cursor: pointer;
}
.btn-back:hover { background-color: #dbeaff; }
</style>
