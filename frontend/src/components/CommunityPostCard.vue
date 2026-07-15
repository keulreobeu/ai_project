<template>
  <div class="post-card" @click="$emit('click')">
    <div class="post-header">
      <h3 class="post-title">{{ post.title }}</h3>
      <span class="post-date">{{ formatDate(post.created_at) }}</span>
    </div>
    <div class="post-meta">
      <span class="post-category">{{ getCategoryLabel(post.category) }}</span>
      <span class="post-views">조회 {{ post.view_count ?? 0 }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CommunityPostCard',
  props: {
    post: {
      type: Object,
      required: true,
    },
  },
  emits: ['click'],
  methods: {
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR');
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
  },
};
</script>

<style scoped>
.post-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.post-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #00aeef;
  transform: translateY(-2px);
}
.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.post-title {
  font-size: 16px;
  font-weight: 600;
  color: #222222;
  margin: 0;
  flex: 1;
  line-height: 1.4;
  word-break: break-word;
}
.post-date {
  font-size: 13px;
  color: #6b7280;
  white-space: nowrap;
}
.post-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.post-category {
  display: inline-block;
  padding: 4px 8px;
  background-color: #e5e7eb;
  color: #222222;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}
.post-views {
  font-size: 13px;
  color: #6b7280;
}
</style>