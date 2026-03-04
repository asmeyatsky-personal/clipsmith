'use client';

import { useState } from 'react';
import { Users, Calendar, Circle, UserPlus, MapPin, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

interface Group {
  id: string;
  name: string;
  description: string;
  memberCount: number;
  category: string;
  isJoined: boolean;
}

interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  location: string;
  attendeeCount: number;
  isRsvped: boolean;
}

interface CreatorCircle {
  id: string;
  name: string;
  creatorCount: number;
  description: string;
}

const mockGroups: Group[] = [
  { id: '1', name: 'Cinematic Creators', description: 'A community for creators who love cinematic storytelling and film techniques.', memberCount: 1243, category: 'Film', isJoined: false },
  { id: '2', name: 'Short-Form Masters', description: 'Tips, tricks, and collaboration for short-form video creators.', memberCount: 3891, category: 'Short-Form', isJoined: true },
  { id: '3', name: 'Music Video Creators', description: 'Connect with fellow music video directors and editors.', memberCount: 872, category: 'Music', isJoined: false },
  { id: '4', name: 'Tutorial Creators Hub', description: 'For creators who teach and educate through video content.', memberCount: 2156, category: 'Education', isJoined: false },
  { id: '5', name: 'Vlog Nation', description: 'Daily vloggers sharing experiences and growing together.', memberCount: 5420, category: 'Vlog', isJoined: true },
  { id: '6', name: 'Gaming Content Creators', description: 'Everything gaming: Let\'s Plays, reviews, esports highlights.', memberCount: 7832, category: 'Gaming', isJoined: false },
];

const mockEvents: Event[] = [
  { id: '1', title: 'Creator Meetup: NYC', description: 'In-person networking event for Clipsmith creators in New York City.', date: '2026-03-15T18:00:00Z', location: 'New York, NY', attendeeCount: 89, isRsvped: false },
  { id: '2', title: 'Live Editing Workshop', description: 'Learn advanced editing techniques in this live virtual workshop.', date: '2026-03-20T14:00:00Z', location: 'Virtual', attendeeCount: 234, isRsvped: true },
  { id: '3', title: 'Short-Form Video Challenge', description: 'Create and submit your best 60-second video for a chance to be featured.', date: '2026-04-01T00:00:00Z', location: 'Virtual', attendeeCount: 512, isRsvped: false },
  { id: '4', title: 'Creator Economy Panel', description: 'Industry experts discuss monetization strategies and the future of creator economy.', date: '2026-04-10T16:00:00Z', location: 'Virtual', attendeeCount: 178, isRsvped: false },
];

const mockCircles: CreatorCircle[] = [
  { id: '1', name: 'Favorite Editors', creatorCount: 12, description: 'My top video editors to follow' },
  { id: '2', name: 'Cooking Channels', creatorCount: 8, description: 'Best cooking content creators' },
  { id: '3', name: 'Tech Reviewers', creatorCount: 15, description: 'Technology review channels I watch' },
];

export default function CommunityPage() {
  const [groups, setGroups] = useState<Group[]>(mockGroups);
  const [events, setEvents] = useState<Event[]>(mockEvents);
  const [circles] = useState<CreatorCircle[]>(mockCircles);

  const toggleJoinGroup = (groupId: string) => {
    setGroups(prev => prev.map(g =>
      g.id === groupId ? { ...g, isJoined: !g.isJoined, memberCount: g.isJoined ? g.memberCount - 1 : g.memberCount + 1 } : g
    ));
  };

  const toggleRsvp = (eventId: string) => {
    setEvents(prev => prev.map(e =>
      e.id === eventId ? { ...e, isRsvped: !e.isRsvped, attendeeCount: e.isRsvped ? e.attendeeCount - 1 : e.attendeeCount + 1 } : e
    ));
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <Users className="text-blue-500" />
        Community
      </h1>

      <Tabs defaultValue="groups">
        <TabsList className="mb-6">
          <TabsTrigger value="groups">Groups</TabsTrigger>
          <TabsTrigger value="events">Events</TabsTrigger>
          <TabsTrigger value="circles">Circles</TabsTrigger>
        </TabsList>

        <TabsContent value="groups">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {groups.map((group) => (
              <Card key={group.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{group.name}</CardTitle>
                  <CardDescription>{group.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1 text-sm text-zinc-500">
                      <Users size={14} />
                      <span>{group.memberCount.toLocaleString()} members</span>
                    </div>
                    <Button
                      variant={group.isJoined ? 'secondary' : 'default'}
                      size="sm"
                      onClick={() => toggleJoinGroup(group.id)}
                      className="gap-1"
                    >
                      <UserPlus size={14} />
                      {group.isJoined ? 'Joined' : 'Join'}
                    </Button>
                  </div>
                  <span className="inline-block mt-2 text-xs px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
                    {group.category}
                  </span>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="events">
          <div className="space-y-4">
            {events.map((event) => (
              <Card key={event.id}>
                <CardContent className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-6">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{event.title}</h3>
                    <p className="text-sm text-zinc-500 mt-1">{event.description}</p>
                    <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-zinc-400">
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {formatDate(event.date)}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin size={14} />
                        {event.location}
                      </span>
                      <span className="flex items-center gap-1">
                        <Users size={14} />
                        {event.attendeeCount} attending
                      </span>
                    </div>
                  </div>
                  <Button
                    variant={event.isRsvped ? 'secondary' : 'default'}
                    onClick={() => toggleRsvp(event.id)}
                  >
                    {event.isRsvped ? 'Cancel RSVP' : 'RSVP'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="circles">
          <div className="mb-6">
            <p className="text-zinc-500 mb-4">Organize the creators you follow into circles for a personalized feed experience.</p>
            <Button variant="default" className="gap-1">
              <Circle size={14} />
              Create New Circle
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {circles.map((circle) => (
              <Card key={circle.id}>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Circle size={16} className="text-blue-500" />
                    {circle.name}
                  </CardTitle>
                  <CardDescription>{circle.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-zinc-500">{circle.creatorCount} creators</span>
                    <Button variant="ghost" size="sm">
                      View
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
