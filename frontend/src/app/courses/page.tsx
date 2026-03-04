'use client';

import { useState } from 'react';
import { GraduationCap, Star, Users, Filter, BookOpen, Clock, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

interface Course {
  id: string;
  title: string;
  creator: string;
  description: string;
  price: number;
  enrollmentCount: number;
  rating: number;
  category: string;
  duration: string;
  lessonCount: number;
  thumbnailUrl?: string;
  isEnrolled: boolean;
}

const courseCategories = ['all', 'editing', 'cinematography', 'storytelling', 'effects', 'audio', 'color', 'business', 'social-media'];

const mockCourses: Course[] = [
  { id: '1', title: 'Master Short-Form Video Editing', creator: 'Alex Chen', description: 'Learn professional editing techniques for TikTok, Reels, and Shorts.', price: 29.99, enrollmentCount: 4521, rating: 4.8, category: 'editing', duration: '4h 30m', lessonCount: 24, isEnrolled: true },
  { id: '2', title: 'Cinematic Color Grading', creator: 'Sarah Kim', description: 'Transform your footage with Hollywood-grade color grading techniques.', price: 49.99, enrollmentCount: 2890, rating: 4.9, category: 'color', duration: '6h 15m', lessonCount: 32, isEnrolled: true },
  { id: '3', title: 'Storytelling for Creators', creator: 'Marcus Johnson', description: 'Craft compelling narratives that keep viewers watching till the end.', price: 19.99, enrollmentCount: 6234, rating: 4.7, category: 'storytelling', duration: '3h 45m', lessonCount: 18, isEnrolled: false },
  { id: '4', title: 'VFX & Motion Graphics Basics', creator: 'Priya Patel', description: 'Add stunning visual effects and motion graphics to your videos.', price: 39.99, enrollmentCount: 1876, rating: 4.6, category: 'effects', duration: '5h 00m', lessonCount: 28, isEnrolled: false },
  { id: '5', title: 'Audio Production for Video', creator: 'Jordan Lee', description: 'Master audio mixing, sound design, and music selection for video content.', price: 24.99, enrollmentCount: 3102, rating: 4.5, category: 'audio', duration: '3h 30m', lessonCount: 20, isEnrolled: false },
  { id: '6', title: 'Monetize Your Content', creator: 'Taylor Swift', description: 'Strategies for building a sustainable income as a content creator.', price: 0, enrollmentCount: 12450, rating: 4.9, category: 'business', duration: '2h 45m', lessonCount: 15, isEnrolled: false },
  { id: '7', title: 'Smartphone Cinematography', creator: 'David Park', description: 'Shoot professional-looking videos with just your phone.', price: 14.99, enrollmentCount: 8932, rating: 4.7, category: 'cinematography', duration: '4h 00m', lessonCount: 22, isEnrolled: false },
  { id: '8', title: 'Social Media Growth Masterclass', creator: 'Emma Wilson', description: 'Proven strategies to grow your audience across all platforms.', price: 34.99, enrollmentCount: 5678, rating: 4.8, category: 'social-media', duration: '5h 30m', lessonCount: 30, isEnrolled: false },
];

export default function CoursesPage() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [courses] = useState<Course[]>(mockCourses);

  const enrolledCourses = courses.filter(c => c.isEnrolled);
  const filteredCourses = courses.filter(c => {
    if (selectedCategory === 'all') return true;
    return c.category === selectedCategory;
  });

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={12}
            className={star <= Math.round(rating) ? 'text-yellow-500 fill-yellow-500' : 'text-zinc-300'}
          />
        ))}
        <span className="text-xs text-zinc-500 ml-1">{rating}</span>
      </div>
    );
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <GraduationCap className="text-blue-500" />
        Courses & Tutorials
      </h1>

      {/* Enrolled Courses */}
      {enrolledCourses.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <BookOpen size={20} />
            Your Enrolled Courses
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {enrolledCourses.map((course) => (
              <Card key={course.id} className="border-blue-200 dark:border-blue-800">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">{course.title}</CardTitle>
                    <CheckCircle size={18} className="text-green-500 flex-shrink-0" />
                  </div>
                  <CardDescription>by {course.creator}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm text-zinc-500">
                    <span className="flex items-center gap-1">
                      <Clock size={14} />
                      {course.duration}
                    </span>
                    <span>{course.lessonCount} lessons</span>
                  </div>
                  <Button variant="default" size="sm" className="w-full mt-3">
                    Continue Learning
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter size={16} className="text-zinc-500" />
          <span className="text-sm font-medium">Filter by Category</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {courseCategories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                selectedCategory === cat
                  ? 'bg-blue-500 text-white'
                  : 'bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700'
              }`}
            >
              {cat === 'all' ? 'All Courses' : cat.charAt(0).toUpperCase() + cat.slice(1).replace('-', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Course Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredCourses.map((course) => (
          <Card key={course.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            {/* Thumbnail Placeholder */}
            <div className="h-36 bg-gradient-to-br from-blue-500/20 to-violet-500/20 flex items-center justify-center rounded-t-xl">
              <GraduationCap size={32} className="text-blue-500/50" />
            </div>
            <CardHeader className="pb-2">
              <CardTitle className="text-base line-clamp-2">{course.title}</CardTitle>
              <CardDescription className="text-xs">by {course.creator}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-zinc-500 line-clamp-2 mb-3">{course.description}</p>
              {renderStars(course.rating)}
              <div className="flex items-center justify-between mt-3">
                <div className="flex items-center gap-1 text-xs text-zinc-400">
                  <Users size={12} />
                  <span>{course.enrollmentCount.toLocaleString()} enrolled</span>
                </div>
                <span className="flex items-center gap-1 text-xs text-zinc-400">
                  <Clock size={12} />
                  {course.duration}
                </span>
              </div>
              <div className="flex items-center justify-between mt-3">
                <span className="font-bold text-sm">
                  {course.price === 0 ? (
                    <span className="text-green-500">Free</span>
                  ) : (
                    `$${course.price.toFixed(2)}`
                  )}
                </span>
                <Button size="sm" variant={course.isEnrolled ? 'secondary' : 'default'}>
                  {course.isEnrolled ? 'Enrolled' : 'Enroll'}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredCourses.length === 0 && (
        <div className="text-center py-12 text-zinc-500">
          No courses found in this category.
        </div>
      )}
    </div>
  );
}
