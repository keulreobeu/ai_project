<template>
  <div class="post-form">
    <h2 class="form-title">새 글쓰기</h2>

    <div class="form-group">
      <label>카테고리</label>
      <select v-model="form.category">
        <option value="general">자유게시판</option>
        <option value="festival">축제</option>
        <option value="restaurant">음식점</option>
        <option value="tips">팁 & 정보</option>
      </select>
    </div>

    <div class="form-group">
      <label>제목</label>
      <input v-model="form.title" type="text" placeholder="제목을 입력하세요" />
    </div>

    <div class="form-group">
      <label>내용</label>
      <textarea v-model="form.content" rows="8" placeholder="내용을 입력하세요"></textarea>
    </div>

    <div class="form-group">
      <label>비밀번호</label>
      <input v-model="form.password" type="password" placeholder="비밀번호를 입력하세요" />
    </div>

    <div class="form-actions">
      <button class="btn-submit" @click="submitForm">작성</button>
      <button class="btn-cancel" @click="$emit('cancel')">취소</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CommunityPostForm',
  emits: ['submit', 'cancel'],
  data() {
    return {
      form: {
        category: 'general',
        title: '',
        content: '',
        password: '',
      },
    };
  },
  methods: {
    submitForm() {
      if (!this.form.title.trim() || !this.form.content.trim() || !this.form.password.trim()) {
        alert('제목, 내용, 비밀번호를 모두 입력해주세요.');
        return;
      }
      this.$emit('submit', {
        category: this.form.category,
        title: this.form.title.trim(),
        content: this.form.content.trim(),
        password: this.form.password.trim(),
      });
    },
  },
};
</script>

<style scoped>
.post-form {
  padding: 24px;
}
.form-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 20px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}
.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #222222;
}
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-group textarea {
  resize: vertical;
}
.form-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 20px;
}
.btn-submit,
.btn-cancel {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.btn-submit {
  background-color: #00aeef;
  color: white;
}
.btn-cancel {
  background-color: #e5e7eb;
  color: #222222;
}
</style>